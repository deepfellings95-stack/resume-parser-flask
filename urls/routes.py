from flask import redirect, render_template, request, Blueprint, current_app, Response, url_for
from werkzeug.utils import secure_filename
from parsers.pypdf2_parser import pdfParser
from parsers.doc_parser import documnetParser
from parsers.image_parser import imageParser
from parsers.text_parser import textParser
from models.chatgpt_response import chatGPTResponse
from urls.save_to_database import Save
from flask_login import current_user
from database_models.posts import Post
import os


upload_bp = Blueprint('urls', __name__)


@upload_bp.route('/pdf/<filename>')
def parsing_pdf(filename):
    try:

        upload_folder = current_app.config['UPLOAD_FOLDER']

        full_filepath = os.path.join(upload_folder, filename)

        reader = pdfParser(full_filepath)
        all_text = reader.extract_all_text()
        if len(all_text) < 100:
            return redirect(url_for('urls.parsing_image', filename = filename))

        gpt = chatGPTResponse(all_text)
        all_text = gpt.get_response()

        saving_file = Save(filename, all_text, user_id = current_user.id)
        result_of_saving = saving_file.save_text()
        print(f"\n\n{result_of_saving}\n\n")
        
        return render_template('result.html', text= all_text, filename = filename)
    except Exception as e:
        return f" Error {e}"
        #return render_template('home.html')

@upload_bp.route('/docx/<filename>')
def parsing_documnets(filename):
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        full_filepath = os.path.join(upload_folder, filename)

        para_text = documnetParser(full_filepath)
        all_text = para_text.extract_all_text()
        if len(all_text) < 100:
            return redirect(url_for('urls.parsing_image', filename = filename))
        gpt = chatGPTResponse(all_text)
        all_text = gpt.get_response()
        
        return render_template('result.html', text= all_text, filename = filename)
    except Exception as e:
        return f" Error {e}"
        #return render_template('home.html')



@upload_bp.route('/image/<filename>')
def parsing_image(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    full_filepath = os.path.join(upload_folder, filename)

    img_text = imageParser(full_filepath)
    all_text = img_text.extract_all_text()

    if isinstance(all_text, str):
        parsed_text = all_text

    elif isinstance(all_text ,dict) and "ParsedResults" in all_text:
        parsed_text = all_text["ParsedResults"][0].get("ParsedText","")
    else:
        parsed_text = ''

    gpt = chatGPTResponse(parsed_text)
    parsed_text = gpt.get_response()
        
    return render_template('result.html', text= parsed_text, filename = filename)

@upload_bp.route('/text/<filename>')
def parsing_text(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    full_filepath = os.path.join(upload_folder, filename)

    text_file_txt = textParser(full_filepath)
    all_text = text_file_txt.extract_all_text()

    gpt = chatGPTResponse(all_text)
    all_text = gpt.get_response()
                        
    return render_template('result.html', text= all_text, filename = filename)

@upload_bp.route('/view/<int:id>')
def view_file(id):
    post = Post.query.get_or_404(id)
    return render_template('result.html', text = post.text, filename = post.filename)






























































                 
