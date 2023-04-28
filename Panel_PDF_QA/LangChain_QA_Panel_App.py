import os
import tempfile
import panel as pn
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

pn.extension('texteditor', template="bootstrap", sizing_mode='stretch_width')

TEMPLATE = """
{% extends base %}
{% block postamble %}
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KyZXEAg3QhqLMpG8r+Knujsl7/1L_dstPt3HV5HzF6Gvk/e3I+WsIffauQ//ybn" crossorigin="anonymous">
{% endblock %}
{% block contents %}
{{ embed(roots.panel) }}
{% endblock %}
"""


# Define file_input and openaikey variables
file_input = pn.widgets.FileInput()
openaikey = pn.widgets.TextInput(value='', placeholder='Enter OpenAI API Key')
output = pn.pane.Markdown("")

question = pn.widgets.TextInput(value='', placeholder='Type your question here')
button = pn.widgets.Button(name='Run')

widgets = pn.Row(question, button)
# Create the Row panel with file_input and openaikey
# row_panel = pn.Row(file_input, openaikey)

# Create the template object and add the row_panel to it
template = pn.Template(TEMPLATE)
template.add_panel('panel', row_panel)


# template = pn.Template(TEMPLATE)
# template.add_panel('panel', pn.Row(file_input, openaikey))

{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "04815d1b-44ee-4bd3-878e-fa0c3bf9fa7f",
   "metadata": {
    "tags": []
   },
   "source": [
    "# LangChain QA Panel App\n",
    "\n",
    "This notebook shows how to make this app:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a181568b-9cde-4a55-a853-4d2a41dbfdad",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "#!pip install langchain openai chromadb tiktoken pypdf panel\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9a464409-d064-4766-a9cb-5119f6c4b8f5",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "import os \n",
    "from langchain.chains import RetrievalQA\n",
    "from langchain.llms import OpenAI\n",
    "from langchain.document_loaders import TextLoader\n",
    "from langchain.document_loaders import PyPDFLoader\n",
    "from langchain.indexes import VectorstoreIndexCreator\n",
    "from langchain.text_splitter import CharacterTextSplitter\n",
    "from langchain.embeddings import OpenAIEmbeddings\n",
    "from langchain.vectorstores import Chroma\n",
    "import panel as pn\n",
    "import tempfile\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b2d07ea5-9ff2-4c96-a8dc-92895d870b73",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "pn.extension('texteditor', template=\"bootstrap\", sizing_mode='stretch_width')\n",
    "pn.state.template.param.update(\n",
    "    main_max_width=\"690px\",\n",
    "    header_background=\"#F08080\",\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "763db4d0-3436-41d3-8b0f-e66ce16468cd",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "file_input = pn.widgets.FileInput(width=300)\n",
    "\n",
    "openaikey = pn.widgets.PasswordInput(\n",
    "    value=\"\", placeholder=\"Enter your OpenAI API Key here...\", width=300\n",
    ")\n",
    "prompt = pn.widgets.TextEditor(\n",
    "    value=\"\", placeholder=\"Enter your questions here...\", height=160, toolbar=False\n",
    ")\n",
    "run_button = pn.widgets.Button(name=\"Run!\")\n",
    "\n",
    "select_k = pn.widgets.IntSlider(\n",
    "    name=\"Number of relevant chunks\", start=1, end=5, step=1, value=2\n",
    ")\n",
    "select_chain_type = pn.widgets.RadioButtonGroup(\n",
    "    name='Chain type', \n",
    "    options=['stuff', 'map_reduce', \"refine\", \"map_rerank\"]\n",
    ")\n",
    "\n",
    "widgets = pn.Row(\n",
    "    pn.Column(prompt, run_button, margin=5),\n",
    "    pn.Card(\n",
    "        \"Chain type:\",\n",
    "        pn.Column(select_chain_type, select_k),\n",
    "        title=\"Advanced settings\", margin=10\n",
    "    ), width=600\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9b83cc06-3401-498f-8f84-8a98370f3121",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "def qa(file, query, chain_type, k):\n",
    "    # load document\n",
    "    loader = PyPDFLoader(file)\n",
    "    documents = loader.load()\n",
    "    # split the documents into chunks\n",
    "    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)\n",
    "    texts = text_splitter.split_documents(documents)\n",
    "    # select which embeddings we want to use\n",
    "    embeddings = OpenAIEmbeddings()\n",
    "    # create the vectorestore to use as the index\n",
    "    db = Chroma.from_documents(texts, embeddings)\n",
    "    # expose this index in a retriever interface\n",
    "    retriever = db.as_retriever(search_type=\"similarity\", search_kwargs={\"k\": k})\n",
    "    # create a chain to answer questions \n",
    "    qa = RetrievalQA.from_chain_type(\n",
    "        llm=OpenAI(), chain_type=chain_type, retriever=retriever, return_source_documents=True)\n",
    "    result = qa({\"query\": query})\n",
    "    print(result['result'])\n",
    "    return result"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2722f43b-daf6-4d17-a842-41203ae9b140",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "# result = qa(\"example.pdf\", \"what is the total number of AI publications?\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "60e1b3d3-c0d2-4260-ae0c-26b03f1b8824",
   "metadata": {},
   "outputs": [],
   "source": [
    "convos = []  # store all panel objects in a list\n",
    "\n",
    "def qa_result(_):\n",
    "    os.environ[\"OPENAI_API_KEY\"] = openaikey.value\n",
    "    \n",
    "    # save pdf file to a temp file \n",
    "    if file_input.value is not None:\n",
    "        file_input.save(\"/.cache/temp.pdf\")\n",
    "    \n",
    "        prompt_text = prompt.value\n",
    "        if prompt_text:\n",
    "            result = qa(file=\"/.cache/temp.pdf\", query=prompt_text, chain_type=select_chain_type.value, k=select_k.value)\n",
    "            convos.extend([\n",
    "                pn.Row(\n",
    "                    pn.panel(\"\\U0001F60A\", width=10),\n",
    "                    prompt_text,\n",
    "                    width=600\n",
    "                ),\n",
    "                pn.Row(\n",
    "                    pn.panel(\"\\U0001F916\", width=10),\n",
    "                    pn.Column(\n",
    "                        result[\"result\"],\n",
    "                        \"Relevant source text:\",\n",
    "                        pn.pane.Markdown('\\n--------------------------------------------------------------------\\n'.join(doc.page_content for doc in result[\"source_documents\"]))\n",
    "                    )\n",
    "                )\n",
    "            ])\n",
    "            #return convos\n",
    "    return pn.Column(*convos, margin=15, width=575, min_height=400)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c3a70857-0b98-4f62-a9c0-b62ca42b474c",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "qa_interactive = pn.panel(\n",
    "    pn.bind(qa_result, run_button),\n",
    "    loading_indicator=True,\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "228e2b42-b1ed-43af-b923-031a70241ab0",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "output = pn.WidgetBox('*Output will show up here:*', qa_interactive, width=630, scroll=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1b0ec253-2bcd-4f91-96d8-d8456e900a58",
   "metadata": {
    "tags": []
   },
   "outputs": [],
   "source": [
    "# layout\n",
    "pn.Column(\n",
    "    pn.pane.Markdown(\"\"\"\n",
    "    ## \\U0001F60A! Question Answering with your PDF file\n",
    "    \n",
    "    1) Upload a PDF. 2) Enter OpenAI API key. This costs $. Set up billing at [OpenAI](https://platform.openai.com/account). 3) Type a question and click \"Run\".\n",
    "    \n",
    "    \"\"\"),\n",
    "    pn.Row(file_input,openaikey),\n",
    "    output,\n",
    "    widgets\n",
    "\n",
    ").servable()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

def create_app():
    return pn.Column(
        pn.pane.Markdown("""
        ## \U0001F60A! Question Answering with your PDF file

        1) Upload a PDF. 2) Enter OpenAI API key. This costs $. Set up billing at [OpenAI](https://platform.openai.com/account). 3) Type a question and click "Run".

        """),
        pn.Row(file_input, openaikey),
        output,
        widgets,
    )

app = create_app()
template.servable(title='LangChain QA Panel App', static_dirs={'/': '.'})
