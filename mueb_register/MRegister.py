import qrcode
import sqlite3
import socketserver
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
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

print("Listening for MUEB DHCP discover")
print("{:<8} {:<17} {:<5}".format("scan", "MAC", "MUEB id"))

prev_MAC = None


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global prev_MAC
        data = self.request[0].strip()
        CHADDR = list(data[28:34])  # CHWADDR
        if(hex(CHADDR[0]) != '0x54' or hex(CHADDR[1]) != '0x10' or hex(CHADDR[2]) != '0xec'):
            return

        MAC = ':'.join(["{0:02X}".format(i) for i in CHADDR])

        # handle multiple requests from the same device
        if prev_MAC != MAC:
            # save to DB
            c.execute("INSERT OR IGNORE INTO mueb(mac) VALUES('{}')".format(MAC))
            conn.commit()

            c.execute("SELECT mueb_id FROM mueb WHERE mac='{}'".format(MAC))
            mueb_id = c.fetchall()[0][0]

            print("{:<8} {:<17} {:<5}".format(
                datetime.now().strftime('%H:%M:%S'), MAC, mueb_id))
            qr.add_data(MAC)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            W, H = img.size

            font = ImageFont.truetype("arial.ttf", 30)
            w, h = font.getsize(MAC)
            caption = MAC+"\n\n{}".format(str(mueb_id).center(32))

            finalImg = Image.new(
                'RGBA', (W+w+qr.border*qr.box_size, H), 'white')
            finalImg.paste(img)

            draw = ImageDraw.Draw(finalImg)
            draw.text((W, (H-(qr.border*qr.box_size))/2),
                      caption, "black", font)

            finalImg.show()
            finalImg.save("{}.png".format(mueb_id))
            qr.clear()

        prev_MAC = MAC


def main():
    with socketserver.UDPServer(('', 67), UDPHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            conn.close()


if __name__ == '__main__':
    main()
