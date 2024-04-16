import React, {useState, useEffect } from 'react'
import './local.css';

const TEST = () => {
    const [name, setName] = useState('')
    const [code, setCode] = useState('')
    const [number, setNumber] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault();
        const user = {name, code, number}
        console.log(user)

       fetch('/test', {
           method: 'POST',
           headers: {"Content-Type":"application/json"},
           body: JSON.stringify(user)
       }).then(() => {
           console.log("Submitted user")
       })
    }

      return (
            <div>
                <form onSubmit={handleSubmit}>
                    <table border={1}>
                        <tbody>
                        <tr>
                            <th>Driver Name</th> <th>Code</th>   <th>Taxi Number</th>  <th>Action</th>
                        </tr>
                                <tr>
                                    <td><input type={'text'} value={name}  id={'name'}  onChange={ (e) => setName(e.target.value)} /></td>
                                    <td><input type={'text'} value={code}  id={'code'}   onChange={ (e) => setCode(e.target.value)}   /></td>
                                    <td><input type={'text'} value={number}  id={'number'}  onChange={ (e) => setNumber(e.target.value)}   /></td>
                                    <td><button type={'submit'}>Action</button></td>
                                </tr>
                        </tbody>
                    </table>
                </form>
            </div>
        )

}

export default TEST