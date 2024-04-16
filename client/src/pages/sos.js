import React, {useState, useEffect } from 'react'
import './local.css';

function SOS(){

    const [data, setData] = useState([{}])

     useEffect(() => {
        fetch("/sos").then(
            res => res.json()
        ).then(
            data => {
                setData(data)
                console.log("data : "+data)
            }
        )
    }, [])



      return (
            <div>
                <form action={'/sos'} method={'POST'}>
                    <table border={1}>
                        <tbody>
                        <tr>
                            <th>Action</th>
                            <th>Driver Name</th>
                            <th>Code</th>
                            <th>Taxi Number</th>
                            <th>SOS Details</th>
                            <th>Start Time</th>
                        </tr>
                        {(typeof data === 'undefined') ? (
                            <p>Loading.....</p>
                        ) : (
                            data.map((member, i) => (
                                <tr>
                                    <td><input type={'radio'} value={member.ID} name={'sosid'}/></td>
                                    <td>{member.FirstName} {member.LastName}</td>
                                    <td>{member.CODE}</td>
                                    <td>{member.TaxiNumber}</td>
                                    <td>{member.SosDetails}</td>
                                    <td>{member.CreatedTime}</td>
                                </tr>
                            ))
                        )}
                        <tr><td colSpan={6} align={'right'}><button type={'submit'}>Action</button></td></tr>
                        </tbody>
                    </table>
                </form>
            </div>
        )


}

export default SOS