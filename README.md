Este repositorio contiene el código fuente de una aplicación diseñada para proporcionar a los usuarios dos funcionalidades principales de manera sencilla: 
la consulta de estadísticas de cualquier club de fútbol y la obtención del valor actual de compra y venta del dólar blue en Argentina.
El proyecto se ha desarrollado integrando diversas herramientas y servicios para ofrecer una experiencia informativa y útil. 
Para la consulta de estadísticas de fútbol, se realiza un web scraping selectivo de fuentes de datos deportivas utilizando la librería Beautiful Soup 4. 
Por otro lado, la obtención del valor del dólar blue se logra mediante la integración con una API pública que proporciona esta información en tiempo real.
Requerimientos: pip install beautifulsoup4, pip install python-dotenv, pip install discord.py
```bash
pip install beautifulsoup4
pip install python-dotenv
pip install discord.py
```
Tambien requiere enlazar el token del bot de discord en un .env, el cual no subi porque se puede utilizar maliciosamente.
