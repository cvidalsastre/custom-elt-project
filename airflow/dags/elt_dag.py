from datetime import datetime, timedelta
from airflow import DAG
from docker.types import Mount
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)


}


def run_elt_script():
    script_path = "opt/airflow/elt/elt_script.py"
    result = subprocess.run(["python", script_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ELT script failed: {result.stderr}")
    else:
        print(result.stdout)


dag = DAG(
    'elt_and_dbt',
    default_args=default_args,
    description='ELT pipeline with dbt',
    start_date=datetime(2024, 9, 19),
    catchup=False,
)

t1 = PythonOperator(
    task_id='run_elt_script',
    python_callable=run_elt_script,
    dag=dag
)

t2 = DockerOperator(
    task_id='dbt_run',
    image='ghcr.io/dbt-labs/dbt:postgres:1.4.7',
    command='["run", "--profiles-dir", "/rooot", "--project-dir", "/dbt"]',
    dag=dag,
    auto_remove=True,
    docker_url="unix://var/run/docker.sock",
    network_mode="bridge",
    mounts=[Mount(source='/home/cris/Documents/dev2024/docker-data-ing/custom-elt-project',
                  target='/dbt',
                  type='bind',
                  ),
            Mount(source='/home/cris/.dbt', target='/root', type='bind')]
)


t1 >> t2
