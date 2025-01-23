import os
from flask import Flask, request, render_template, redirect, url_for
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    llm_response = ''
    
    if request.method == 'POST':
        
        api_key = request.form.get('apikey')
        
        pdf_file = request.files.get('pdfFile')

        if api_key and pdf_file:

            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
            pdf_file.save(pdf_path)
            
            llm_response = process_with_llm(pdf_path, api_key)

            #return redirect(url_for('index', llm_response=llm_response))

    return render_template('index.html', llm_response=llm_response)


def process_with_llm(file_path, api_key):

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        sample_file = genai.upload_file(path=file_path, display_name="My File PDF")

        PROMPT_TEMPLATE = '''
            You are given the extracted text from a PDF file. Your task is to extract and present all the relevant information from the
            PDF file with precision. Follow these instructions:

            1. Extract the text exactly as it appears in the PDF, including spaces, line breaks, and indentation. Do not modify the text
            or add any extra information.

            2. If the text includes tabular data (such as tables or lists), extract the data in a way that preserves the table structure
            and formatting. Format it as tabular data with rows and columns, using proper delimiters (like commas or tabs) between the
            cells. Ensure that the data remains aligned and clear.

            3. For any numbered or bulleted lists, preserve the order and structure exactly as it appears in the PDF.

            4. If the document includes headings or subheadings, keep them distinct and formatted as they appear in the original PDF,
            making sure to preserve their hierarchy.

            5. Do **not** add any additional commentary, summaries, or explanations. Your output should only include the extracted content
            from the PDF, structured as closely to the original as possible.

            6. If there is any non-text content like images or other embedded media, do not include them in the output.

            7. If there are any hyperlinks, include the text as it is. Preserve the hyperlink format, and output the exact text (anchor text) as seen in the PDF, with no alterations.

            Output the text in plain text format, maintaining all formatting such as indentation, newlines, tabular data, and hyperlinks in a consistent and readable structure.
        '''


        response = model.generate_content([sample_file, PROMPT_TEMPLATE])

        print(response.text)

        return response.text
        
    except Exception as e:
        return f"An error occurred while processing: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
