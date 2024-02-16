import {  useState } from "react";
import axios from 'axios'

function App() {
  const [file,setFile]=useState(null)
  const [pyFile,setPyFile]=useState(null)
  const [functionName,setFunctionName]=useState('')
  const [outputFile,setOutputFile]=useState('')
  const [progress,setProgress]=useState(0)
  const [showProgress,setShowProgress]=useState(false)
  const [error,setError]=useState(null)

  const submitHandler=async(e)=>{
    setError(null)
    e.preventDefault()
    if (file){
      setProgress(0)
      setShowProgress(true)
      let n=0
      const interval=setInterval(()=>{
         n+=1
        axios.get('http://localhost:5000/progress')
        .then(response=>{
          if (n<=2 && response.data.progress==100){
            setProgress(0)
          }
          else{
            setProgress(response.data.progress)
          }
          console.log(progress)
          if (response.data.progress==100){
            setProgress(100)
            console.log(progress)
            axios.get('http:///localhost:5000/reset')
            .then(response=>{
              console.log(response)
              clearInterval(interval)
            }).catch(err=>{
              console.log(err)
            })
          }
          if (progress==100){
            clearInterval(interval)
          }
        })
        .catch(err=>{
          setError(err)
          setShowProgress(false)
          setOutputFile('')
        })
        
      },30)
      
      const formData=new FormData();
      console.log(file, pyFile, functionName)
      if (!(file) || !(pyFile) || functionName==''){
        setError('Please fill all fields')
        clearInterval(interval)
        setShowProgress(false)
        setOutputFile('')
      }
      else{
        formData.append('inputfile',file)
        formData.append('pyfile',pyFile)
        formData.append('funcName', functionName)
      // responseType: 'blob',
      try{
        
        const response=await axios.post('http://localhost:5000/processing', formData,{
        headers:{
        'Content-Type': 'multipart/form-data',
        }
      })
      // if (response.status==400){
      //   const error_obj=await response.data.text()
      //   console.log(error_obj)
      //   const err=JSON.parse(error_obj).error
      //   console.log(err)
      //   clearInterval(interval)
      // }
      const url=window.URL.createObjectURL(new Blob([response.data]))
      setOutputFile(url)
      setShowProgress(false)
      console.log('uploaded')
      console.log(showProgress)
      }
      catch(e){
        const data=await e.response.data
        console.log(e.response.data.error)
        setError(data.error)
        setShowProgress(false)
        setOutputFile('')
        clearInterval(interval)
      }
      }

      
      
    }
  }
  return (
    <div className="App">
      <h1 className="heading">CSV UTILITY</h1>
      <div className="input">
        <form className='form' onSubmit={submitHandler}>
          <div className="input-div"><label className="input-label">Input CSV File: </label>
          <input className='input-file' accept=".csv" type='file' onChange={(e)=>setFile(e.target.files[0])}/>

          <label className="input-label">Input Python File for data manipulation</label>
          <input className='input-file' accept=".py" type='file' onChange={(e)=>setPyFile(e.target.files[0])}/>
          <label className="input-label">Specify the name of function to be called on each row of data: </label>
          <p className="eg">E.g: def manipulate(row):<br></br>
                <span className='tab'/>processed=[] <br></br>
                <span className='tab'/>for i in row:<br></br>
                <span className='tab'/><span className='tab'/>processed.append(i.upper())<br/>
                <span className='tab'/>return processed <br></br>
                  </p>
          <input className="input-text" type='text' valeu={functionName} placeholder="e.g manipulate" onChange={(e)=>{
            setFunctionName(e.target.value)
          }}></input>
          </div>
          <button className='btn' type="submit">Process</button>
        </form>
      </div>
      {showProgress &&  (
        <div className="progress">
          <p className="progress-text">Processing... {progress}</p>
        </div>
        )}
        {outputFile && <div className="output">
          <p>Download Result: </p>
          <a className='download' href={outputFile} download='output.csv'>Result</a>
        </div>}
        {error && <div className="error">
            <p className="error-text">Error: {error}</p>
          </div>}
    </div>
  );
}

export default App;
