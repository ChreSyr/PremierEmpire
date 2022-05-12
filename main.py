
import baopig as bp


app = bp.Application(name="PremierEmpire", theme="dark", size=(1000, 700))
menu = bp.Scene(app)
btn = bp.Button(parent=menu, text="Hi !", background_color="green4")


if __name__ == "__main__":
    app.launch()
