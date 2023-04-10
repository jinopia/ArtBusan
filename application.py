import sys
import openai
import deepl
import json
from flask import Flask, redirect, render_template, request, url_for, jsonify

application = Flask(__name__)

openai.api_key = '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'

deepl_api_key = "279f30c8-3cd5-b20a-e4e1-9a24f732f45a:fx"
translator = deepl.Translator(deepl_api_key)

size_big = "1024x1024"
size_middle = "512x512"
size_small = "256x256"

@application.route("/", methods=["GET"])
def hello():
    return "Hello Docent ver2!"

@application.route("/sample", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        animal = request.form["animal"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(animal),
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)

@application.route("/image_page", methods=("GET", "POST"))
def image_page():
    if request.method == "POST":
        prompt = request.form["prompt"]
        object = request.form["object"]
        style = request.form["style"]
        size_string = request.form["size_string"]

        if (prompt != None or object != None) and style != None:
            image_urls = generateImages(prompt, object, style, size_string)
            return render_template("image.html", image_urls=image_urls)
        else:
           render_template("image.html") 
    
    return render_template("image.html")

@application.route("/image_gen", methods=['POST'])
def image_gen():
    params = request.get_json()

    prompt = params['prompt']
    objectForImage = params['object']
    style = params['style']
    size = params['size']
        
    return jsonify({
        'images': generateImages(prompt, objectForImage, style, size)
    })

def generateImages(prompt_src, object, style, size):
    result_prompt = ''
    if prompt_src != None:
        translated_prompt = translator.translate_text(prompt_src, target_lang = "en-US")
        result_prompt = f'Draw \'{translated_prompt}\' in {style} style'
    else:
        result_prompt = f'Draw \'{object}\' in {style} style'

    size_string = get_size_string(size)
    
    response = openai.Image.create(
        prompt = result_prompt,
        n = 4,
        size = size_string
    )
    
    image_urls = [response['data'][0]['url'], 
                 response['data'][1]['url'], 
                 response['data'][2]['url'], 
                 response['data'][3]['url']]
    
    return image_urls

def get_size_string(size):
    if size == "small":
        return size_small
    elif size == "middle":
        return size_middle
    else:
        return size_big
    
def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.

Animal: Cat
Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
Animal: Dog
Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
Animal: {}
Names:""".format(
        animal.capitalize()
    )

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(sys.argv[1]))
