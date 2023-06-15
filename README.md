# Visualization 2
Implementation of a 2D spatial distribution visualization based on Zhao et. al, "Phoenixmap: An Abstract Approach to Visualize 2D Spatial Distributions", 2020 (https://arxiv.org/abs/2002.00732). 

---

### The application is deployed to Streamlit:
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://phoenixmap.streamlit.app)
https://phoenixmap.streamlit.app


---


### Project structure
- Documentation: `doc/`
- HTML for Hall-of-Fame: `html/`
- Screenshot for Hall-of-Fame: `./screenshot.jpg`
- Code: `src/`
- Compiled binaries: [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://phoenixmap.streamlit.app)

####
- Streamlit app: `src/app/`  
- Phoenixmap polygons: `src/app/ressources/`
- Phoenixmap polygons generator: `src/generator/`



----
##### (Run locally)
###### Setup
Go into src/:
```
cd src/
```
Create python virtual environment:
```
python -m venv env
```

Install requirements:
```
source env/bin/activate
pip install -r requirements.txt
```

###### Usage
Generate polygons:
```
python generator/phoenixmap_generator.py
```

Start application:
```
streamlit run app/page_intro.py
```


