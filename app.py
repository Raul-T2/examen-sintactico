from flask import Flask, render_template, request, jsonify
import ply.yacc as yacc
import re

app = Flask(__name__)

# Diccionario de entidades de nacimiento
ENTIDADES = {
    "AS": "AGUASCALIENTES", "BC": "BAJA CALIFORNIA", "BS": "BAJA CALIFORNIA SUR", 
    "CC": "CAMPECHE", "CL": "COAHUILA", "CM": "COLIMA", "CS": "CHIAPAS", "CH": "CHIHUAHUA", 
    "DF": "DISTRITO FEDERAL", "DG": "DURANGO", "GT": "GUANAJUATO", "GR": "GUERRERO", 
    "HG": "HIDALGO", "JC": "JALISCO", "MC": "MÉXICO", "MN": "MICHOACÁN", "MS": "MORELOS", 
    "NT": "NAYARIT", "NL": "NUEVO LEÓN", "OC": "OAXACA", "PL": "PUEBLA", "QT": "QUERÉTARO", 
    "QR": "QUINTANA ROO", "SP": "SAN LUIS POTOSÍ", "SL": "SINALOA", "SR": "SONORA", 
    "TC": "TABASCO", "TS": "TAMAULIPAS", "TL": "TLAXCALA", "VZ": "VERACRUZ", "YN": "YUCATÁN", 
    "ZS": "ZACATECAS", "NE": "NACIDO EN EL EXTRANJERO"
}

# Definición de tokens
tokens = (
    'LETRAS',
    'NUMEROS'
)

# Reglas para los tokens
t_LETRAS = r'[A-Z]'
t_NUMEROS = r'[0-9]'

# Regla para manejar errores
def t_error(t):
    t.lexer.skip(1)

# Construcción del lexer
import ply.lex as lex
lexer = lex.lex()

# Definir el análisis sintáctico usando yacc
def p_curp(p):
    '''curp : LETRAS LETRAS LETRAS LETRAS NUMEROS NUMEROS NUMEROS NUMEROS NUMEROS NUMEROS LETRAS LETRAS LETRAS LETRAS LETRAS NUMEROS'''
    p[0] = p[1:]

def p_error(p):
    pass

# Construcción del parser
parser = yacc.yacc()

# Función para desglosar la CURP
def analizar_curp(curp):
    # Asegurar que la CURP sea de 18 caracteres y en mayúsculas
    if len(curp) != 18 or not curp.isalnum() or not curp.isupper():
        return [], [], "La CURP es inválida: debe contener exactamente 18 caracteres alfanuméricos en mayúsculas."

    # Desglose de tokens de la CURP en sus partes
    tokens = [
        curp[:2],             # Apellido paterno
        curp[2],              # Apellido materno
        curp[3],              # Inicial del nombre
        curp[4:6],            # Año de nacimiento
        curp[6:8],            # Mes de nacimiento
        curp[8:10],           # Día de nacimiento
        curp[10],             # Género
        curp[11:13],          # Entidad de nacimiento
        curp[13],             # Consonante interna del apellido paterno
        curp[14],             # Consonante interna del apellido materno
        curp[15],             # Consonante interna del primer nombre
        curp[16:18]           # Homoclave (RENAPO)
    ]

    # Mapeo de descripciones para cada sección de la CURP
    descripcion = [
        "Apellido paterno",
        "Apellido materno",
        "Inicial del nombre",
        "Año de nacimiento",
        "Mes de nacimiento",
        "Día de nacimiento",
        "Género: Masculino" if curp[10] == "H" else "Género: Femenino",
        f"Entidad de nacimiento: {ENTIDADES.get(curp[11:13], 'Entidad desconocida')}",
        "Consonante interna del apellido paterno",
        "Consonante interna del apellido materno",
        "Consonante interna del primer nombre",
        "Homoclave (RENAPO)"
    ]

    # Validación sintáctica
    resultado = parser.parse(curp)
    if not resultado:
        mensaje = "La CURP es válida y tiene un formato correcto."
    else:
        mensaje = "La CURP tiene un formato incorrecto."

    return tokens, descripcion, mensaje

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el procesamiento de la CURP
@app.route('/analizar', methods=['POST'])
def analizar():
    curp = request.json['curp'].strip().upper()
    tokens, descripcion, mensaje = analizar_curp(curp)

    # Contar letras y números
    total_numeros = sum(c.isdigit() for c in curp)
    total_letras = sum(c.isalpha() for c in curp)

    return jsonify({
        'tokens': tokens,
        'descripcion': descripcion,
        'mensaje': mensaje,
        'total_numeros': total_numeros,
        'total_letras': total_letras
    })

if __name__ == '__main__':
    app.run(debug=True)
