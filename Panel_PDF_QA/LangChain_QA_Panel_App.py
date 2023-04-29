import os 
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import panel as pn
import tempfile

pn.extension('texteditor', template="bootstrap", sizing_mode='stretch_width')
pn.state.template.param.update(
    main_max_width="690px",
    header_background="#F08080",
)
file_input = pn.widgets.FileInput(width=300)

openaikey = pn.widgets.PasswordInput(
    value="", placeholder="Enter your OpenAI API Key here...", width=300
)
prompt = pn.widgets.TextEditor(
    value="", placeholder="Enter your questions here...", height=160, toolbar=False
)
run_button = pn.widgets.Button(name="Run!")

select_k = pn.widgets.IntSlider(
    name="Number of relevant chunks", start=1, end=5, step=1, value=2
)
select_chain_type = pn.widgets.RadioButtonGroup(
    name='Chain type', 
    options=['stuff', 'map_reduce', "refine", "map_rerank"]
)

widgets = pn.Row(
    pn.Column(prompt, run_button, margin=5),
    pn.Card(
        "Chain type:",
        pn.Column(select_chain_type, select_k),
        title="Advanced settings", margin=10
    ), width=600
)
def qa(file, query, chain_type, k):
    # load document
    loader = PyPDFLoader(file)
    documents = loader.load()
    # split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    # select which embeddings we want to use
    embeddings = OpenAIEmbeddings()
    # create the vectorestore to use as the index
    db = Chroma.from_documents(texts, embeddings)
    # expose this index in a retriever interface
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})
    # create a chain to answer questions 
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(), chain_type=chain_type, retriever=retriever, return_source_documents=True)
    result = qa({"query": query})
    print(result['result'])
    return result
# result = qa("example.pdf", "what is the total number of AI publications?")
convos = []  # store all panel objects in a list

def qa_result(_):
    os.environ["OPENAI_API_KEY"] = openaikey.value
    
    # save pdf file to a temp file 
    if file_input.value is not None:
        file_input.save("/.cache/temp.pdf")
    
        prompt_text = prompt.value
        if prompt_text:
            result = qa(file="/.cache/temp.pdf", query=prompt_text, chain_type=select_chain_type.value, k=select_k.value)
            convos.extend([
                pn.Row(
                    pn.panel("\U0001F60A", width=10),
                    prompt_text,
                    width=600
                ),
                pn.Row(
                    pn.panel("\U0001F916", width=10),
                    pn.Column(
                        result["result"],
                        "Relevant source text:",
                        pn.pane.Markdown('\n--------------------------------------------------------------------\n'.join(doc.page_content for doc in result["source_documents"]))
                    )
                )
            ])
            #return convos
    return pn.Column(*convos, margin=15, width=575, min_height=400)
qa_interactive = pn.panel(
    pn.bind(qa_result, run_button),
    loading_indicator=True,
)
output = pn.WidgetBox('*Output will show up here:*', qa_interactive, width=630, scroll=True)
# layout
pn.Column(
    pn.pane.Markdown("""
    ## \U0001F60A! Question Answering with your PDF file
    
    1) Upload a PDF. 2) Enter OpenAI API key. This costs $. Set up billing at [OpenAI](https://platform.openai.com/account). 3) Type a question and click "Run".
    
    """),
    pn.Row(file_input,openaikey),
    output,
    widgets

).servable()