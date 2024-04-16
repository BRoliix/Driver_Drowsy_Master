import './local.css';
import React, {useState, useEffect } from 'react'



function Session(){

     const chkStatus = (val) => {
           if(val === null) return "Active"
            else return "SOS Actioned"
        }


    const [data, setData] = useState([{}])

    useEffect(() => {
        fetch("/session").then(
            res => res.json()
        ).then(
            data => {
                setData(data)
                console.log(data)
            }
        )
    }, [])

    return (
        <div>
            <table border={1}><tbody>

                <tr>
                    <th>Driver Name</th><th>Taxi Number</th><th>Start Time</th><th>End Time</th><th>Status</th>
                </tr>
            {(typeof data === 'undefined') ? (
                <p>Loading.....</p>
            ) : (
                data.map((member, i) => (
                    <tr>
                        <td>{member.FirstName} {member.LastName}</td><td>{member.TaxiNumber}</td><td>{member.StartTime}</td><td>{member.EndTime}</td>
                        <td>{member.Status}</td>
                    </tr>
                ))
            )}
        </tbody></table>
        </div>
    )
}

export default Session

