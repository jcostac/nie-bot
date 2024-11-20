import funciones_bot as fb
import pretty_errors 

if __name__ == "__main__":
    bot = fb.NieBot()
    bot.select_province("Madrid")
    oficina = bot.check_oficinas("Madrid", "any")
    bot.submit_tramite_form(oficina)
    bot.seleccionar_tipo_presentacion()
