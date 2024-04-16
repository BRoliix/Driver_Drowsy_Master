import mysql.connector
import time
from datetime import datetime
import pandas as pd


def connect():
    cnx = mysql.connector.connect(user='root', password='Rohil7203',
                                  host='127.0.0.1',
                                  database='rohil')
    return cnx


def connect_ro():
    cnx = mysql.connector.connect(user='root', password='Database_sucks55',
                                  host='192.168.87.155',
                                  database='DRIVER_DROWSINESS')
    return cnx


def check():
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    var = (datetime.now() + pd.DateOffset(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    print(var)

    query = "SELECT `sos`.`id`,  `sos`.`taxiid`, `sos`.`driverid`, `sos`.`details`, `sos`.`status`," \
            "  `sos`.`createdtime`,  `sos`.`actionedtime`,  `sos`.`sessionid` FROM `DRIVER_DROWSINESS`.`sos`"

    cnx = connect_ro()
    cursor = cnx.cursor()
    cursor.execute(query)

    res = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    print(res)
    # return res


def session_details():
    cnx = connect()
    cursor = cnx.cursor()
    query = "select t.number as TaxiNumber , u.firstname as FirstName, u.lastname as LastName, u.code as Code," \
            "DATE_FORMAT(s.starttime, '%Y-%m-%d %H:%M:%S') as StartTime, DATE_FORMAT(s.endtime, '%Y-%m-%d %H:%M:%S') as EndTime, ss.actionedTime as Status " \
            "FROM rohil.session s LEFT JOIN rohil.sos ss ON s.id = ss.sessionId , rohil.taxi t, rohil.user u " \
            "WHERE s.taxiid = t.id and s.userid = u.id and u.type = 'Driver'  and u.status='Active'"
    print(query)
    cursor.execute(query)
    res = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    print(res)
    for row in res:
        if row['Status'] is None:
            row.update({'Status': 'Active'})
        else:
            row.update({'Status': 'SOS Actioned'})
    print(res)
    # return cursor.fetchall()
    return res


def sos_details(sid=None):
    print(sid)
    if sid is not None:
        action_sos(sid)

    query = "select s.id as ID, u.firstName as FirstName, u.lastName as LastName, t.number as TaxiNumber, u.code as CODE, s.details as SosDetails," \
            " DATE_FORMAT(s.createdTime, '%Y-%m-%d %H:%M:%S') as CreatedTime, DATE_FORMAT(s.actionedTime, '%Y-%m-%d %H:%M:%S') as ActionedTime" \
            " FROM rohil.sos s, rohil.taxi t, rohil.user u " \
            "WHERE s.taxiid = t.id and s.driverid = u.id and u.type = 'Driver' and u.status='Active'" \
            "AND s.actionedTime IS NULL"

    cnx = connect()
    cursor = cnx.cursor()
    cursor.execute(query)

    res = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    print(res)
    return res


def raise_sos():
    print("Raise SOS ......")
    cnx = connect()
    cursor = cnx.cursor()
    query = """INSERT INTO rohil.sos(`taxiid`, `driverid`, `details`, `status`, `createdtime`, `actionedtime`) VALUES
     (1,1, 'Driver immobilized at Yishun blk 11. Please check Priority 5', 'NEW', '2023-06-06 011:00:00','2023-06-06 11:03:00')"""

    cursor.execute(query)
    cnx.commit()

    cursor.close()
    cnx.close()


def action_sos(sid):
    cnx = connect()
    cursor = cnx.cursor()

    date = time.strftime('%Y-%m-%d %H:%M:%S')
    print(date)
    query = "UPDATE rohil.sos SET actionedTime = '" + time.strftime('%Y-%m-%d %H:%M:%S') + "' WHERE id =" + sid

    cursor.execute(query)
    cnx.commit()

    cursor.close()
    cnx.close()


def login(pid, taxi, password):
    print(" Driver logged in")
    uquery = "SELECT status FROM rohil.user where password ='" + password + "' and id = " + pid

    pquery = "SELECT id FROM rohil.taxi WHERE number='" + taxi + "'"
    cnx = connect()
    cursor = cnx.cursor(buffered=True)
    cursor.execute(uquery)
    urowcount = cursor.rowcount
    cursor.execute(pquery)
    taxiid = cursor.fetchone()[0]
    print(urowcount)
    print(taxiid)
    if urowcount > 0 & taxiid is not None:
        d1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        d2 = (datetime.now() + pd.DateOffset(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        print(d1)
        print(d2)

        query = "INSERT INTO rohil.session (taxiid, userid, starttime, endtime) VALUES (" + str(taxiid) + ", " + str(pid) + " , '" + d1 + "','" + d2 + "')"

        print(query)
        cursor.execute(query)
        cnx.commit()

    cursor.close()
    cnx.close()

def admlogin(pid, password):
    print(" Driver logged in")
    uquery = "SELECT status FROM rohil.user where password ='" + password + "' and id = " + pid
    cnx = connect()
    cursor = cnx.cursor()
    cursor.execute(uquery)
    res = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    print(res)
    return res


class DAO:
    if __name__ == "__main__":
        # raise_sos()
        check()