# "Saving and loading" multiple FAISS indices in a single store is not supported: https://github.com/deepset-ai/haystack/issues/3554
from src.schema import IndexORM


def upsert_index(session, index_name, urls):
    index = session.query(IndexORM).filter(IndexORM.name == index_name).first()
    if index is None:
        index = IndexORM(name=index_name, urls=urls)
        session.add(index)
    else:
        for url in urls:
            if url not in index.urls:
                index.urls.append(url)
    session.commit()


def get_all_indices(session):
    return session.query(IndexORM).all()


def run_indexing_pipeline(pipeline, index_name, urls, depth):
    pipeline.run(
        params={
            "Crawler": {"urls": urls, "crawler_depth": depth},
            "Shaper": {"meta": {"index_name": index_name}},
        }
    )


def run_query_pipeline(
    pipeline, query, index_name, prompt_template="question-answering"
):
    return pipeline.run(
        query,
        params={
            "Prompter": {"prompt_template": prompt_template},
            "Shaper": {
                "meta": {"index_name": index_name} if index_name is not None else {}
            },
        },
    )


def add_metadata_to_documents(documents, meta):
    for doc in documents:
        doc.meta = {**doc.meta, **meta}
    return documents


def filter_documents_by_metadata(documents, meta={}):
    filtered_documents = []
    for doc in documents:
        if all([doc.meta.get(key) == value for key, value in meta.items()]):
            filtered_documents.append(doc)
    return filtered_documents
