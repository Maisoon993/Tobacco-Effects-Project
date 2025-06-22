# Tobacco Effects Project
An interactive Streamlit application that analyzes the effect of tobacco use on mortality rates worldwide using WHO data. It provides key metrics, global maps, time-series trends, income-group breakdowns, top-country rankings, and stacked tobacco use indicator visualizations.

### 1. Project Structure
```
├── data/
│   ├── rep_gho_tobacco/
│   │   ├── data.xlsx            # Tobacco prevalence data
│   │   └── metadata.pdf
│   └── rep_ihme_inc/
│       ├── data.xlsx            # Disease incidence/mortality data
│       └── metadata-ihme-gbd.pdf
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── streamlit.toml              # Streamlit configuration
└── README.md                   # This documentation
```

### 2. Getting Started
1. Clone the repository
```
git clone https://github.com/Maisoon993/Tobacco-Effects-Project.git
cd Tobacco-Effects-Project
```
3. Install dependencies
```
pip install -r requirements.txt
```
5. Run locally
```
streamlit run app.py
```
Open your browser at http://localhost:8501 to view the dashboard.

### 3. Data Sources
- Tobacco Prevalence: Tobacco smoking prevalence by country, sex, and year (WHO Global Health Observatory).
- Mortality/Incidence: Age-standardized mortality incidence by country, sex, and year (WHO Global Health Observatory).
- All raw Excel files are stored under the data/ directory.

### 4. Features
- KPIs: Average tobacco prevalence and mortality rate, broken down by sex.
- Global Map: Choropleth of Tracheal, bronchus, and lung cancer mortality rates by country.
- Time-Series: Actual and forecasted tobacco prevalence & mortality trends, side-by-side for males and females.
- Income-Group: Donut charts showing average tobacco prevalence and Tracheal, bronchus, and lung cancer mortality rates by World Bank income tiers.
- Top Countries: Bar charts for top 5 countries with highest prevalence and mortality.
- Stacked Indicators: Comparison of multiple tobacco-use indicators (adolescent vs adult, cigarettes vs e-cigarettes vs smokeless) over time, separated by sex.

### 5. Deployment
This app is deployed on Streamlit Cloud:
[https://tobacco-effects-project.streamlit.app/](https://tobacco-effects-project.streamlit.app/)

