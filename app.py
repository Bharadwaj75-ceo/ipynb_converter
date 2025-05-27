import os
import json
import requests
from flask import (
    Flask, request, render_template, redirect, url_for, flash,
    send_from_directory, after_this_request, session
)
from werkzeug.utils import secure_filename
import nbformat
from nbconvert import HTMLExporter
import openai
import markdown2
import tempfile
import uuid
from playwright.sync_api import sync_playwright
import asyncio
import aiohttp
import concurrent.futures
from functools import lru_cache
import time
from dotenv import load_dotenv
load_dotenv()
# Configuration
UPLOAD_FOLDER = 'uploads'
PDF_TEMP_FOLDER = 'pdf_temp'
ALLOWED_EXTENSIONS = {'ipynb'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PDF_TEMP_FOLDER'] = PDF_TEMP_FOLDER
app.config['SECRET_KEY'] = 'your_very_secret_key_for_flask_session_and_flashes_v2'

if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PDF_TEMP_FOLDER): os.makedirs(PDF_TEMP_FOLDER)

OPENROUTER_API_KEY = os.getenv("aPI_KEY")
OPENROUTER_MODELS_LIST = []
# DEFAULT_OPENROUTER_MODELS will be a list now
DEFAULT_OPENROUTER_MODELS = ["openai/gpt-3.5-turbo"]  # Default is a list

# Simple mapping for provider logos (assumes files in static/images/logos/)
PROVIDER_LOGOS = {
    "openai": "openai.png",
    "anthropic": "anthropic.png",
    "google": "google.png",
    "meta": "meta.png",
    "mistralai": "mistralai.png",
    "cohere": "cohere.png",
    # Add more as needed
    "default": "default_logo.png"
}

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY environment variable not found!")


def get_provider_from_model_id(model_id):
    """Extracts provider from model_id like 'openai/gpt-3.5-turbo' -> 'openai'"""
    if "/" in model_id:
        return model_id.split("/")[0].lower()
    # Handle cases like 'mistralai:mistral-tiny' if OpenRouter uses colons
    if ":" in model_id:
        return model_id.split(":")[0].lower()
    return "default"  # Fallback


def get_code_explanation_openrouter_async(code_string, model_id, session):
    """Async version of the explanation function"""
    if not OPENROUTER_API_KEY:
        return "<p><em>OpenRouter API key not configured.</em></p>"

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_id,
            "messages": [
                {"role": "system",
                 "content": "You are a highly skilled AI assistant. Explain the Python code cell. Your explanation must be VERY CONCISE (1-3 sentences), summarizing its primary function and key operations. Use Markdown for clarity (e.g., backticks for code terms). Avoid excessive detail or stating the obvious."},
                {"role": "user", "content": f"Explain this Python code cell:\n\n```python\n{code_string}\n```"}
            ],
            "temperature": 0.2,
            "max_tokens": 100
        }

        async def make_request():
            async with session.post("https://openrouter.ai/api/v1/chat/completions",
                                    json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    explanation = data['choices'][0]['message']['content'].strip()
                    return markdown2.markdown(explanation, extras=["fenced-code-blocks", "tables", "break-on-newline"])
                else:
                    error_text = await response.text()
                    return f"<p><em>API Error with model '{model_id}': HTTP {response.status} - {error_text}</em></p>"

        return asyncio.create_task(make_request())

    except Exception as e:
        print(f"Error creating async request for model {model_id}: {e}")
        return f"<p><em>Error with model '{model_id}': {e}</em></p>"


async def process_all_explanations_async(notebook_cells, selected_model_ids):
    """Process all explanations concurrently using async"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        cell_model_mapping = []

        # Create all tasks upfront
        for cell_idx, (code_source, code_html) in enumerate(notebook_cells):
            for model_id in selected_model_ids:
                task = get_code_explanation_openrouter_async(code_source, model_id, session)
                if asyncio.iscoroutine(task) or hasattr(task, '__await__'):
                    tasks.append(task)
                    cell_model_mapping.append((cell_idx, model_id))

        # Execute all tasks concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []

        # Organize results back into the expected structure
        processed_cells = [{'code_html': code_html, 'explanations_by_model': []}
                           for _, code_html in notebook_cells]

        for i, result in enumerate(results):
            if i < len(cell_model_mapping):
                cell_idx, model_id = cell_model_mapping[i]

                # Handle exceptions
                if isinstance(result, Exception):
                    explanation_html = f"<p><em>Error with model '{model_id}': {str(result)}</em></p>"
                else:
                    explanation_html = result

                # Get model display name
                model_info = next((m for m in OPENROUTER_MODELS_LIST if m['id'] == model_id), None)
                model_name_for_display = model_info['name'] if model_info and model_info.get('name') else model_id

                processed_cells[cell_idx]['explanations_by_model'].append({
                    'model_id': model_id,
                    'model_name': model_name_for_display,
                    'explanation_html': explanation_html
                })

        return processed_cells


def get_code_explanation_openrouter_threaded(code_string, model_id):
    """Thread-safe version using requests (fallback if async doesn't work)"""
    if not OPENROUTER_API_KEY:
        return "<p><em>OpenRouter API key not configured.</em></p>"

    try:
        import requests

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_id,
            "messages": [
                {"role": "system",
                 "content": "You are a highly skilled AI assistant. Explain the Python code cell. Your explanation must be VERY CONCISE (1-3 sentences), summarizing its primary function and key operations. Use Markdown for clarity (e.g., backticks for code terms). Avoid excessive detail or stating the obvious."},
                {"role": "user", "content": f"Explain this Python code cell:\n\n```python\n{code_string}\n```"}
            ],
            "temperature": 0.2,
            "max_tokens": 100
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            explanation = data['choices'][0]['message']['content'].strip()
            return markdown2.markdown(explanation, extras=["fenced-code-blocks", "tables", "break-on-newline"])
        else:
            return f"<p><em>API Error with model '{model_id}': HTTP {response.status_code} - {response.text}</em></p>"

    except Exception as e:
        print(f"Error in threaded request for model {model_id}: {e}")
        return f"<p><em>Error with model '{model_id}': {e}</em></p>"


def process_explanations_with_threading(notebook_cells, selected_model_ids, max_workers=10):
    """Process explanations using ThreadPoolExecutor for concurrency"""
    processed_cells = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_info = {}

        for cell_idx, (code_source, code_html) in enumerate(notebook_cells):
            cell_futures = []
            for model_id in selected_model_ids:
                future = executor.submit(get_code_explanation_openrouter_threaded, code_source, model_id)
                future_to_info[future] = (cell_idx, model_id)
                cell_futures.append(future)

        # Organize results
        cell_results = {}
        for future in concurrent.futures.as_completed(future_to_info):
            cell_idx, model_id = future_to_info[future]

            if cell_idx not in cell_results:
                cell_results[cell_idx] = {'explanations': []}

            try:
                explanation_html = future.result()
            except Exception as e:
                explanation_html = f"<p><em>Error with model '{model_id}': {str(e)}</em></p>"

            # Get model display name
            model_info = next((m for m in OPENROUTER_MODELS_LIST if m['id'] == model_id), None)
            model_name_for_display = model_info['name'] if model_info and model_info.get('name') else model_id

            cell_results[cell_idx]['explanations'].append({
                'model_id': model_id,
                'model_name': model_name_for_display,
                'explanation_html': explanation_html
            })

    # Convert to expected format
    for cell_idx, (code_source, code_html) in enumerate(notebook_cells):
        explanations = cell_results.get(cell_idx, {}).get('explanations', [])
        processed_cells.append({
            'code_html': code_html,
            'explanations_by_model': explanations
        })

    return processed_cells


@lru_cache(maxsize=128)
def get_cached_html_for_cell(cell_source_hash):
    """Cache HTML conversion for identical code cells"""
    # This would need to be implemented with actual caching logic
    pass


def fetch_openrouter_models():
    global OPENROUTER_MODELS_LIST
    if not OPENROUTER_API_KEY:
        OPENROUTER_MODELS_LIST = [];
        print("Cannot fetch models: API key missing.");
        return
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        response.raise_for_status()
        models_data = response.json().get("data", [])

        processed_models = []
        for model in models_data:
            provider = get_provider_from_model_id(model.get("id", ""))
            model['provider'] = provider
            model['logo'] = PROVIDER_LOGOS.get(provider, PROVIDER_LOGOS["default"])
            processed_models.append(model)

        OPENROUTER_MODELS_LIST = sorted(
            processed_models,
            key=lambda x: (x.get("name") is None, x.get("name", x.get("id", "")).lower())
        )
        print(f"Fetched {len(OPENROUTER_MODELS_LIST)} models from OpenRouter.")
    except Exception as e:
        print(f"Error fetching/processing OpenRouter models: {e}")
        OPENROUTER_MODELS_LIST = []


fetch_openrouter_models()



# ... (allowed_file, convert_ipynb_to_html_body, home, upload_file - remain largely the same)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_ipynb_to_html_body(notebook_node):
    html_exporter = HTMLExporter(template_name='basic')
    html_exporter.exclude_input_prompt = True;
    html_exporter.exclude_output_prompt = True
    (body, _) = html_exporter.from_notebook_node(notebook_node)
    return body


@app.route('/', methods=['GET'])
def home(): return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'ipynb_file' not in request.files:
        flash('No file part in the request.', 'error');
        return redirect(url_for('home'))
    file = request.files['ipynb_file']
    if file.filename == '':
        flash('No file selected.', 'error');
        return redirect(url_for('home'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        saved_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_filepath)
        try:
            with open(saved_filepath, 'r', encoding='utf-8') as f:
                notebook_node = nbformat.read(f, as_version=4)
            html_body = convert_ipynb_to_html_body(notebook_node)
            return render_template('preview.html', html_content=html_body, original_filename=filename)
        except Exception as e:
            flash(f'Error during HTML conversion: {str(e)}', 'error')
            if os.path.exists(saved_filepath): os.remove(saved_filepath)
            return redirect(url_for('home'))
    else:
        flash('Invalid file type.', 'error');
        return redirect(url_for('home'))


@app.route('/explain', methods=['GET', 'POST'])
def explain_code_page():
    if request.method == 'POST':
        if 'ipynb_file' not in request.files:
            flash('No file part in the request.', 'error')
            return redirect(url_for('explain_code_page'))

        file = request.files['ipynb_file']
        selected_model_ids = request.form.getlist('selected_model_ids')
        if not selected_model_ids:
            selected_model_ids = session.get('selected_model_ids', DEFAULT_OPENROUTER_MODELS)
        session['selected_model_ids'] = selected_model_ids

        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('explain_code_page'))

        if file and allowed_file(file.filename):
            if not OPENROUTER_API_KEY:
                flash('OpenRouter API key not configured.', 'error')
                return redirect(url_for('explain_code_page'))
            if not OPENROUTER_MODELS_LIST:
                flash('AI model list unavailable. Trying to re-fetch...', 'warning')
                fetch_openrouter_models()
                if not OPENROUTER_MODELS_LIST:
                    flash('Still unable to fetch AI models. Please check server logs.', 'error')
                    return redirect(url_for('explain_code_page'))

            original_filename = secure_filename(file.filename)
            try:
                start_time = time.time()

                notebook_content = file.stream.read().decode('utf-8')
                notebook_node = nbformat.reads(notebook_content, as_version=4)

                # Pre-process all code cells
                notebook_cells = []
                html_exporter = HTMLExporter(template_name='basic')
                html_exporter.exclude_input_prompt = True
                html_exporter.exclude_output_prompt = True

                for cell_idx, cell in enumerate(notebook_node.cells):
                    if cell.cell_type == 'code':
                        code_source = cell.source
                        if not code_source.strip():
                            continue

                        temp_nb_node = nbformat.v4.new_notebook(cells=[cell])
                        (code_html, _) = html_exporter.from_notebook_node(temp_nb_node)
                        notebook_cells.append((code_source, code_html))

                if not notebook_cells:
                    flash('No code cells found or all were empty.', 'info')
                    return redirect(url_for('explain_code_page'))

                print(f"Processing {len(notebook_cells)} cells with {len(selected_model_ids)} models...")

                # Try async first, fall back to threading
                try:
                    # Use asyncio for concurrent processing
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    processed_notebook_cells = loop.run_until_complete(
                        process_all_explanations_async(notebook_cells, selected_model_ids)
                    )
                    loop.close()
                    print("Used async processing")
                except Exception as e:
                    print(f"Async processing failed, falling back to threading: {e}")
                    # Fall back to threading
                    processed_notebook_cells = process_explanations_with_threading(
                        notebook_cells, selected_model_ids, max_workers=8
                    )
                    print("Used threaded processing")

                processing_time = time.time() - start_time
                print(f"Total processing time: {processing_time:.2f} seconds")

                flash(f'Generated explanations using {len(selected_model_ids)} model(s) in {processing_time:.1f}s!',
                      'success')

                # Prepare data for tabs
                selected_models_for_tabs = []
                for model_id in selected_model_ids:
                    model_data = next((m for m in OPENROUTER_MODELS_LIST if m['id'] == model_id), None)
                    model_name = model_data.get('name', model_id) if model_data else model_id
                    selected_models_for_tabs.append({'id': model_id, 'name': model_name})

                return render_template('explain.html',
                                       processed_cells=processed_notebook_cells,
                                       filename=original_filename,
                                       selected_models_for_tabs=selected_models_for_tabs)

            except Exception as e:
                flash(f'Error processing notebook: {str(e)}', 'error')
                return redirect(url_for('explain_code_page'))
        else:
            flash('Invalid file type.', 'error')
            return redirect(url_for('explain_code_page'))

    # GET request
    current_selected_ids = session.get('selected_model_ids', DEFAULT_OPENROUTER_MODELS)
    return render_template('explain_upload_form.html',
                           models=OPENROUTER_MODELS_LIST,
                           current_selected_ids=current_selected_ids)

@app.route('/download_pdf/<original_filename>')
def download_pdf(original_filename):
    # ... (Full PDF generation logic from your last working app.py) ...
    ipynb_filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(original_filename))
    if not os.path.exists(ipynb_filepath):
        flash('Original notebook file not found for PDF.', 'error');
        return redirect(url_for('home'))
    try:
        with open(ipynb_filepath, 'r', encoding='utf-8') as f:
            notebook_node = nbformat.read(f, as_version=4)
        html_body_content = convert_ipynb_to_html_body(notebook_node)
        onedark_css_path = os.path.join(app.static_folder, 'css', 'onedark.css')
        with open(onedark_css_path, 'r', encoding='utf-8') as f_css:
            onedark_css_content = f_css.read()
        full_html_for_pdf = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Notebook PDF</title><style>{onedark_css_content} @media print {{html, body {{width: auto !important; height: auto !important;overflow: visible !important; margin: 0 !important; padding: 0 !important;-webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;background-color: #282c34 !important;}}.navbar, .download-pdf-container {{ display: none !important; }}.page-content {{ padding-top: 0 !important; margin: 0 !important;width: 100% !important;}}.page-content .container {{max-width: 8.2in !important;width: 100% !important; margin: 10px auto !important; padding: 15px !important;box-shadow: none !important; border-radius: 0 !important;background-color: #21252b !important; overflow: visible !important;}}img, svg, table, pre {{max-width: 100% !important; page-break-inside: avoid !important;display: block !important;overflow: visible !important;}}div.output_png img, div.output_jpeg img, div.output_gif img, div.output_svg svg {{max-width: 100% !important; height: auto !important;object-fit: contain;}}table {{display: table !important;width: 100% !important;max-width: 100% !important;overflow-x: hidden !important;font-size: 8pt !important;margin: 1em auto !important;border: 1px solid #4b5263 !important;box-shadow: none !important;border-radius: 0 !important;}}table th, table td {{white-space: normal !important; word-break: break-word;padding: 6px 8px !important;vertical-align: top !important;border: 1px solid #4b5263 !important;line-height: 1.3 !important;}}table thead th {{background-color: #353b45 !important;color: #e0e2e6 !important;font-weight: 600 !important;border-bottom: 2px solid #61afef !important;position: static !important;}}table tbody tr:nth-child(even) {{background-color: #2c313a !important;}}table tbody tr:hover {{ background-color: transparent !important; }}table th.pd-index, table th.row_heading {{background-color: #2c313a !important;color: #98c379 !important;border-right: 1px solid #56b6c2 !important;position: static !important;}}table td.pd-index, table td.row_heading {{background-color: #2c313a !important;color: #98c379 !important;border-right: 1px solid #56b6c2 !important;position: static !important;}}table tbody tr:nth-child(even) td.pd-index,table tbody tr:nth-child(even) td.row_heading {{background-color: #2c313a !important;}}div.input_area pre, div.output_area pre {{white-space: pre-wrap !important; word-break: break-all !important;font-size: 0.85em !important;}}}} .container {{max-width: 8.2in; margin: 20px auto; padding: 20px;background-color: #21252b; border-radius: 8px;box-shadow: 0 4px 15px rgba(0,0,0,0.2);}}</style></head><body><div class="page-content"><div class="container" id="pdfContentRoot">{html_body_content}</div></div></body></html>"""
        unique_id = str(uuid.uuid4())
        temp_html_path = os.path.join(tempfile.gettempdir(), f"notebook_render_{unique_id}.html")
        pdf_output_path = os.path.join(app.config['PDF_TEMP_FOLDER'],
                                       f"{os.path.splitext(original_filename)[0]}_{unique_id}.pdf")
        with open(temp_html_path, "w", encoding="utf-8") as f_html:
            f_html.write(full_html_for_pdf)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page_width_px = int(8.2 * 96);
            context = browser.new_context(viewport={'width': page_width_px, 'height': 768}, device_scale_factor=1)
            page = context.new_page();
            page.goto(f"file://{os.path.abspath(temp_html_path)}")
            content_height_px = page.evaluate("document.body.scrollHeight") + 50
            pdf_options = {'path': pdf_output_path, 'print_background': True, 'width': f'{page_width_px}px',
                           'height': f'{content_height_px}px',
                           'margin': {'top': '0px', 'bottom': '0px', 'left': '0px', 'right': '0px'}, 'page_ranges': '1'}
            page.emulate_media(media="print");
            page.pdf(**pdf_options);
            browser.close()
        if os.path.exists(temp_html_path): os.remove(temp_html_path)

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(pdf_output_path): os.remove(pdf_output_path)
                if os.path.exists(ipynb_filepath): os.remove(ipynb_filepath)
            except Exception as error:
                app.logger.error("Error removing file: %s", error)
            return response

        return send_from_directory(app.config['PDF_TEMP_FOLDER'], os.path.basename(pdf_output_path), as_attachment=True,
                                   download_name=f"{os.path.splitext(original_filename)[0]}_pageless.pdf")
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        if 'temp_html_path' in locals() and os.path.exists(temp_html_path): os.remove(temp_html_path)
        if 'pdf_output_path' in locals() and os.path.exists(pdf_output_path): os.remove(pdf_output_path)
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)