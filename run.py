from app import app
import config
app.run(debug=config.Config.DEBUG)