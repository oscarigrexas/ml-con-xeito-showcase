from datetime import datetime

import dlt
from dlt.sources.rest_api import rest_api_source
from prefect import flow


@flow(log_prints=True)
def load_air_quality() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_air_quality",
        destination="filesystem",
        dataset_name="rest_api_data",
    )

    air_quality_source = rest_api_source(
        {
            "client": {"base_url": "https://air-quality-api.open-meteo.com/v1/"},
            "resource_defaults": {
                "endpoint": {
                    "params": {},
                },
            },
            "resources": [
                {
                    "write_disposition": "append",
                    "name": "air-quality",
                    "primary_key": "time",
                    "endpoint": {
                        "data_selector": "hourly",
                        "path": "air-quality",
                        "params": {
                            "latitude": 42.2328,
                            "longitude": -8.7226,
                            "hourly": "carbon_monoxide,carbon_dioxide,nitrogen_dioxide,sulphur_dioxide,ozone,dust,methane,european_aqi",
                            "end_date": datetime.now().strftime("%Y-%m-%d"),
                            # "start_date": "2024-10-01",
                            "start_date": {
                                "type": "incremental",
                                "cursor_path": "time",
                                "initial_value": "2024-01-01",
                                "convert": lambda iso_str: iso_str.split("T")[0],
                            },
                        },
                    },
                    "max_table_nesting": 1,
                },
            ],
        }
    )

    def yield_map(item):
        for values in zip(*item.values()):
            value_array = {k: v for k, v in zip(item.keys(), values)}
            if value_array["european_aqi"] > 30:
                value_array["is_sick"] = 1
            else:
                value_array["is_sick"] = 0
            yield value_array

    air_quality_source.resources["air-quality"].add_yield_map(yield_map)

    load_info = pipeline.run(air_quality_source)
    print(load_info)
