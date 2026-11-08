import sys

from olaf import app, olaf_run, olaf_setup, render_olaf_template, rest_api
from ion.services.services import BatteryHeaterService, LogsMainService
from ion.resources.green_board import GreenBoardResource


@rest_api.app.route('/ion-db')
def ion_db_template():
    """Ion Dashboard"""
    return render_olaf_template('ion_db.html', name='Ion0 Dashboard')

def main():
    """Ion0 OLAF app main"""
    print("Hello from ion!")

    # set up project configuration
    if "--bus" not in sys.argv and "-b" not in sys.argv:
        sys.argv.extend(["--bus", "can0"])
    olaf_setup("c3")
    
    # load template for flask
    rest_api.add_template('src/templates/ion_db.html')

    # add resources (CAN data tx/rx)
    app.add_resource(GreenBoardResource())


    # add services (systemd)
    app.add_service(BatteryHeaterService())
    app.add_service(LogsMainService())

    # run!
    olaf_run()


if __name__ == "__main__":
    main()
