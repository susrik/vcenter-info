import vcenter_info
import logging

logging.basicConfig(level=logging.DEBUG)

app = vcenter_info.create_app()

if __name__ == '__main__':
    app.run(host='::', port='19191')
