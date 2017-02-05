from SimpleCV import Camera
import zbarlight
import sqlite3
import time
import pifacecad
import upload as up
import db_write as db

cam = Camera()
cad = pifacecad.PiFaceCAD()
conn=sqlite3.connect('attendance.db')
cursor=conn.cursor()
scan_mode = 'Attendance'
prev_code = ''
url = 'http://aatserver.appspot.com/sendpresence'

def msg_display(msg_id, stdid=0):
    cad.lcd.clear()
    cad.lcd.set_cursor(0, 0)
    if msg_id == 1:
        cad.lcd.write("Mode: " + scan_mode)
    elif msg_id == 2:
        cad.lcd.write("StudentId: " + stdid +"\n" + scan_mode[0:3] + ' markd online')
    elif msg_id == 3:
        cad.lcd.write("StudentId: " + stdid +"\n" + scan_mode[0:3] + ' markd offline')
    elif msg_id == 4:
        cad.lcd.write("StudentId: " + stdid +"\n" + 'Att marked already')
    elif msg_id == 5:
        cad.lcd.write("Data synced\n successfully!")
    elif msg_id == 6:
        cad.lcd.write("Data sync\n failed!")
    elif msg_id == 7:
        cad.lcd.write("No offline data\n available!")




def switch_mode(event):
    global scan_mode
    global prev_code
    if event.pin_num == 0:
        scan_mode = 'Attendance'
        prev_code = ''
        msg_display(1)
    elif event.pin_num == 1:
        scan_mode = 'Presentation'
        prev_code = ''
        msg_display(1)
    elif event.pin_num == 2:
        scan_mode = 'Upload'
        prev_code = ''
        msg_display(1)


cad.lcd.backlight_on()
cad.lcd.clear()
cad.lcd.set_cursor(0, 0)
cad.lcd.write("ASE Attendance\n System")
time.sleep(2)
listener = pifacecad.SwitchEventListener(chip=cad)
listener.register(0, pifacecad.IODIR_FALLING_EDGE, switch_mode)
listener.register(1, pifacecad.IODIR_FALLING_EDGE, switch_mode)
listener.register(2, pifacecad.IODIR_FALLING_EDGE, switch_mode)
listener.activate()
db.purge_data(cursor)
conn.commit()
cad.lcd.clear()
cad.lcd.set_cursor(0, 0)
cad.lcd.write("Old data purged!")
time.sleep(1)
msg_display(1)
i = 0


try:
    while(scan_mode is not None):
        i += 1
        print(str(i) +' - Scanning in ' + scan_mode + ' Mode')
        if scan_mode != 'Upload':
            img = cam.getImage().getPIL()
            code = zbarlight.scan_codes('qrcode', img)
            if code is not None and code[0] != prev_code and len(code[0]) == 30 \
                    and code[0].startswith('#$#') and code[0].endswith('#$#'):
                prev_code = code[0]
                print('QR code: %s' %prev_code)
                count = db.save_data_offline(cursor, scan_mode, prev_code[3:27])
                conn.commit()
                if count==1:
                    off_data = db.get_offline_data(cursor)
                    data_sync = up.post_data(url, off_data)
                    if data_sync == 1:
                        db.update_sync_records(cursor)
                        msg_display(2,prev_code[3:7])
                    else:
                        msg_display(3,prev_code[3:7])
                else:
                    msg_display(4,prev_code[3:7])
                time.sleep(2.5)
                msg_display(1)
        else:
            print('in upload mode')
            off_data = db.get_offline_data(cursor)
            print(off_data['attendance'])
            if len(off_data['attendance']) > 0:
                print(str(len(off_data['attendance'])))
                data_sync = up.post_data(url, off_data)
                if data_sync == 1:
                    db.update_sync_records(cursor)
                    msg_display(5)
                else:
                    msg_display(6)
            else:
                msg_display(7)
            time.sleep(5)
            msg_display(1)
        time.sleep(0.01)

except KeyboardInterrupt:
    listener.deactivate()
    conn.close()
    exit()
