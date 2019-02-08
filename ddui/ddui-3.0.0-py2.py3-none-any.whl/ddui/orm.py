

def airflow_dags():
    """
    Read the list of dags from Airflow's metastore DB and return the list as a pandas.DataFrame
    :return: pandas.DataFrame
    """
    import pandas as pd
    from airflow import models, settings
    from airflow.settings import Session

    session = Session()
    DM = models.DagModel
    # read orm_dags from the db
    qry = session.query(DM)
    con = session.connection()
    dags_df = pd.read_sql(str(qry.statement), con.connection)

    def filter_outdated_dags(dags_df):
        dagbag = models.DagBag(settings.DAGS_FOLDER)
        outdated_dags = []
        for _, row in dags_df.iterrows():
            dag_id = row["dag_id"]
            dag = dagbag.get_dag(dag_id)
            if not hasattr(dag, "roots"):
                outdated_dags.append(dag_id)

        return dags_df[~dags_df["dag_id"].isin(outdated_dags)]

    return filter_outdated_dags(dags_df).reset_index(drop=True)