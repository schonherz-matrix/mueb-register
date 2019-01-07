import qrcode
import socket
import sqlite3
from PIL import Image, ImageDraw, ImageFont

def main():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    conn = sqlite3.connect("MUEB_register.db")
    c = conn.cursor()

    # create mueb table
    try:
        c.execute('''
        CREATE TABLE mueb (
            mueb_id INTEGER     PRIMARY KEY,
            mac     STRING (17) UNIQUE
                                NOT NULL
        );
        ''')
    except:
        pass

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 67))

    prev_MAC = None
    id = 0

    print("Listening for MUEB DHCP discover")
    print("{:<5} {:<20} {:<5}".format("scan", "MAC", "MUEB id"))

    while 1:
        # wait for dhcp packet
        data = s.recv(1024)
        tmp = list(data[28:34])
        if(hex(tmp[0]) != '0x54' or hex(tmp[1]) != '0x10' or hex(tmp[2]) != '0xec'):
            continue

        MAC = ':'.join(["{0:02X}".format(i) for i in list(data[28:34])])

        # save to DB
        c.execute("INSERT OR IGNORE INTO mueb(mac) VALUES('{}')".format(MAC))
        conn.commit()

        c.execute("SELECT mueb_id FROM mueb WHERE mac='{}'".format(MAC))
        mueb_id = c.fetchall()[0][0]

        print("{:<5} {:<20} {:<5}".format(id, MAC, mueb_id))
        id += 1

        # handle multiple requests
        if prev_MAC != MAC:
            qr.add_data(MAC)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            width, height = img.size

            finalImg = Image.new('RGBA', (width, height), 'white')
            finalImg.paste(img)

            caption = MAC+"/{}".format(mueb_id)
            font = ImageFont.truetype("arial.ttf", 15)
            w, h = font.getsize(caption)

            draw = ImageDraw.Draw(finalImg)
            draw.text((round((width-w)/2), round(height-h-10)),
                    caption, "black", font)

            finalImg.show()
            finalImg.save("{}.png".format(mueb_id))
            qr.clear()
        prev_MAC = MAC

if __name__ == '__main__':
    main()
