from flask import Flask, request, send_file, Response, jsonify, make_response, current_app
from flask_cors import CORS
import os
import ast
import importlib
import json

import csv
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool




app=Flask(__name__)
CORS(app, resources={r"/processing": {"origins": "http://localhost:3000"},r"/progress": {"origins": "http://localhost:3000"},r"/reset": {"origins": "http://localhost:3000"}})
processed=0
no_of_chunks=1
def update_progress():
    global processed, no_of_chunks
    print(processed, no_of_chunks,)

    return round(processed/no_of_chunks * 100,1)

@app.route('/progress')
def progress():
    return jsonify({'progress': update_progress()})

@app.route('/reset')
def reset():
    global processed, no_of_chunks
    processed=0
    no_of_chunks=1
    return Response(status=200)


def process(chunk, content, function_name):
    index,chunk_data=chunk
    output=f'chunk_{index}.csv'
    functions=importlib.import_module('assets.files.function')
    with open(output,'w',newline='') as outfile:
        writer=csv.writer(outfile)
        func=None
        try:
            if (hasattr(functions,function_name)):
                func=getattr(functions,function_name)
            else:
                raise ValueError(f"Function '{function_name}' not found")
        except Exception as e: 
            raise e

        
        for row in chunk_data:
            try:
                result=func(row)
                writer.writerow(result)
            except Exception as e:
                raise e
                
            
    return output



def divide_csv(input_file, codeContent,function_name,size, divisions):
    with open(f'./assets/files/{input_file}','r', newline='') as f:
        reader=csv.reader(f)
        x=next(reader)
        index=1
        chunks=[] #all chunks
        current=[] #current chunk
        for i,row in enumerate(reader):
            current.append(row)
            if i!=0 and i%size==0:
                chunks.append([index, current[:]])
                index+=1
                current.clear()
        
      

        if current:
            chunks.append([index, current[:]])

        '''with ThreadPoolExecutor(max_workers=divisions) as executor:
            results=executor.map(process,chunks)'''
       

        global no_of_chunks
        no_of_chunks=len(chunks)
        global processed
        processed=0

        with Pool(processes=divisions) as p:
            results=[]
            for chunk in chunks:
                result=p.apply_async(process, (chunk,codeContent,function_name))
                results.append(result)
            files=[]
            for result in results:
                try:
                    result_data=result.get()
                    files.append(result.get())
                    processed+=1
                except Exception as e:
                    print('here2')
                    print(files)
                    p.terminate()
                    current_directory = os.path.dirname(os.path.abspath(__file__))

                    # Get a list of all files in the current directory
                    files = os.listdir(current_directory)
                    for file in files:
                        if file.startswith('chunk'):
                            file_path = os.path.join(current_directory, file)
                            # Delete the file
                            os.remove(file_path)
                    raise e
        final_file='output.csv'


        #consolidating output file
        with open(final_file, 'w', newline='') as final:
            writer=csv.writer(final)
            writer.writerow(x)
            for file in files:
                with open(file,'r',newline='') as f:
                    reader=csv.reader(f)
                    for row in reader:
                        writer.writerow(row)
        
        for file in files:
            os.remove(file)

        return final_file


def validate(pyfile):
    f=open(pyfile,'r')
    content=f.read()
    print(content)
    try:
        tree=ast.parse(content)
        print(tree)

        for node in ast.walk(tree):
            if isinstance(node,ast.FunctionDef):
                return True
        return False
    except SyntaxError:
        return False


@app.route("/processing",methods=['POST'])
def processing():
    global processed, no_of_chunks
    processed=0
    no_of_chunks=1
    inputfile=request.files['inputfile']
    pyfile=request.files['pyfile']
    funcName=request.form.get('funcName')

    print(funcName)
    inputfile.save('./assets/files/input.csv')
    pyfile.save('./assets/files/function.py')
    print(inputfile)
    isValid=validate('./assets/files/function.py')
    print(1)
    if not(isValid):
        print('error')
        response_data=json.dumps({"error": "Error occurred in the Python file. Please check syntax and make sure you have your manipulation function."})
        return Response(response_data, status=400, mimetype='application/json')
    else:
        try:
            final=divide_csv('input.csv','function.py',funcName,2000,5)
            return send_file(final, as_attachment=True)
        except Exception as e:
            print(str(e))
            if ('NoneType' in str(e)):
                response_data=json.dumps({"error": "Please check your python function. Make sure it returns an updated row."})
                return Response(response_data,status=400)
            response_data=json.dumps({"error": str(e)})
            return Response(response_data,status=400)
        


if __name__=="__main__":
    app.run(debug=False)