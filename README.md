
# 📘 Wikipedia Link Network Explorer

**Explore how people and topics are connected on Wikipedia through outgoing and simulated incoming links.**  
This tool builds an interactive **3D network graph** using Wikipedia data and visualizes it with Streamlit and Plotly.

## 🚀 Demo

🔗 [Live App on Streamlit Cloud](https://your-app-url.streamlit.app)  
📷 Screenshot: *(add screenshot if available)*

## 📦 Features

- 🔗 Fetch real-time **outgoing** and **incoming** Wikipedia links
- 📊 Calculate **PageRank** centrality
- 🌐 Display a **3D network graph** using Plotly
- 🧠 Filter by gender and search for people
- 📉 Analyze gender and occupation distributions

## 🛠️ Tech Stack

- Python 🐍  
- Streamlit 📺  
- NetworkX 🔗  
- Wikipedia-API 📚  
- Plotly 📈  
- Pandas 🐼  

## 📂 Folder Structure

```
wiki_network_dashboard/
├── streamlit_app.py                    # Main Streamlit app
├── latin_american_intellectuals.csv    # Sample CSV data
├── requirements.txt                    # Python dependencies
└── README.md                           # Project info
```

## 🧰 Installation

1. Clone the repo:
```bash
git clone https://github.com/yourusername/wiki_network_dashboard.git
cd wiki_network_dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run streamlit_app.py
```

## 🌐 Deploy to Streamlit Cloud

1. Push this repo to GitHub  
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)  
3. Click "New App" → Select your repo and file `streamlit_app.py`  
4. Click **Deploy** 🚀

## 🧪 Example Queries

Try searching for:  
- `Gabriela Mistral`  
- `Pablo Neruda`  
- `Octavio Paz`  

## 🧠 Research Context

This project is part of a research study on **epistemic inequality and network visibility** in Wikipedia.  
It highlights the role of structural links in shaping public knowledge.

## 📄 License

MIT License. Free to use and adapt. Please cite the project if it helps your work.
