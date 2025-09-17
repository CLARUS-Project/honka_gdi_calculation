"""
This module defines the Airflow DAG for the Red Wine MLOps lifecycle. The DAG includes tasks
for various stages of the pipeline, including data reading, data processing, model training, 
and selecting the best model. 

The tasks are defined as functions and executed within the DAG. The execution order of the tasks 
is defined using task dependencies.

Note: The actual logic inside each task is not shown in the code, as it may reside in external 
script files.

The DAG is scheduled to run every day at 12:00 AM.


Please ensure that the necessary dependencies are installed and accessible for executing the tasks.

test
"""

from datetime import datetime
from airflow.decorators import dag, task
from kubernetes.client import models as k8s
from airflow.models import Variable


@dag(
    description='MLOps lifecycle production',
    schedule_interval=None, 
    start_date=datetime(2022, 1, 1),
    catchup=False,
    tags=['gdi'],
) 
def honka_gdi_calculation_as_is():

    env_vars={ 
        "POSTGRES_GDI_USERNAME": Variable.get("POSTGRES_GDI_USERNAME"),
        "POSTGRES_GDI_PASSWORD": Variable.get("POSTGRES_GDI_PASSWORD"),
        "POSTGRES_GDI_DATABASE": Variable.get("POSTGRES_GDI_DATABASE"),
        "POSTGRES_GDI_HOST": Variable.get("POSTGRES_GDI_HOST"),
        "POSTGRES_GDI_PORT": Variable.get("POSTGRES_GDI_PORT"),
        "TRUE_CONNECTOR_EDGE_IP": Variable.get("CONNECTOR_EDGE_IP"),
        "TRUE_CONNECTOR_EDGE_PORT": Variable.get("IDS_EXTERNAL_ECC_IDS_PORT"),
        "TRUE_CONNECTOR_CLOUD_IP": Variable.get("CONNECTOR_CLOUD_IP"),
        "TRUE_CONNECTOR_CLOUD_PORT": Variable.get("IDS_PROXY_PORT"),
        "MLFLOW_ENDPOINT": Variable.get("MLFLOW_ENDPOINT"),
        "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
        "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
        "container": "docker",
        "pilot": "HONKA",
        "MLFLOW_EXPERIMENT": "honka_as_is",

    }

    volume_mount = k8s.V1VolumeMount(
        name="dag-dependencies", mount_path="/git"
    )

    init_container_volume_mounts = [
        k8s.V1VolumeMount(mount_path="/git", name="dag-dependencies")
    ]
    
    volume = k8s.V1Volume(name="dag-dependencies", empty_dir=k8s.V1EmptyDirVolumeSource())

    init_container = k8s.V1Container(
        name="git-clone",
        image="alpine/git:latest",
        command=["sh", "-c", "mkdir -p /git && cd /git && git clone -b main --single-branch https://github.com/CLARUS-Project/honka_gdi_calculation.git"],
        volume_mounts=init_container_volume_mounts
    )

    # Define as many task as needed
    @task.kubernetes(
        image='clarusproject/dag-image:1.0.0-slim',
        name='read_data',
        task_id='read_data',
        namespace='airflow',
        init_containers=[init_container],
        volumes=[volume],
        volume_mounts=[volume_mount],
        do_xcom_push=True,
        env_vars=env_vars
    )
    def read_data_procces_task():
        import sys

        sys.path.insert(1, '/git/honka_gdi_calculation/src')
        from Data.read_data import read_data

        return read_data()
    

    @task.kubernetes(
        image='clarusproject/dag-image:1.0.0-slim',
        name='calculate_gdi_index',
        task_id='calculate_gdi_index',
        namespace='airflow',
        init_containers=[init_container],
        volumes=[volume],
        volume_mounts=[volume_mount],
        do_xcom_push=True,
        env_vars=env_vars
    )
    def calculate_gdi_index_task(data):
        import sys

        sys.path.insert(1, '/git/honka_gdi_calculation/src')
        from GDI.GDI_Calculator import calculate_green_deal_index

        index = calculate_green_deal_index(data)

        return index
    
    @task.kubernetes(
        image='clarusproject/dag-image:1.0.0-slim',
        name='store_gdi',
        task_id='store_gdi',
        namespace='airflow',
        init_containers=[init_container],
        volumes=[volume],
        volume_mounts=[volume_mount],
        do_xcom_push=True,
        env_vars=env_vars
    )
    def store_gdi_task(gdi_data):
        import sys
        import os

        sys.path.insert(1, '/git/honka_gdi_calculation/src')
        from DB.store import store_gdi

        # Assuming 'pilot' is a variable that needs to be passed
        pilot = os.getenv('pilot', 'default_pilot')
        store_gdi(pilot, gdi_data)


    # Instantiate each task and define task dependencies
    processing_result = read_data_procces_task()
    calculate_gdi_result = calculate_gdi_index_task(processing_result)
    store_gdi_result = store_gdi_task(calculate_gdi_result)

    # Define the order of the pipeline
    processing_result >> calculate_gdi_result >> store_gdi_result

# Call the DAG
honka_gdi_calculation_as_is()
