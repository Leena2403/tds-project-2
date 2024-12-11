from credentials import *
# in case credentials file don't get imported i am also importing functions separately 
from dotenv import load_dotenv
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
load_dotenv()
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import sys
from sklearn.impute import SimpleImputer
import requests



def get_description(data):
    '''
        to get all data analysis, including strings, numbers etc.
    '''
    return data.describe(include="all")

# Load the dataset
def load_data():
    try:
        return pd.read_csv(sys.argv[1])
    except UnicodeDecodeError:
        return pd.read_csv(sys.argv[1], encoding='ISO-8859-1')
    except:
        raise Exception("Dataset file is missing. Use: uv run autolysis.py <CSV FILE PATH>")



# Summary statistics visualization 
def summary_statistics_plot():
    numeric_data = data.select_dtypes(include=['number'])
    if numeric_data.empty:
        print("No numeric columns available for summary statistics.")
        return
    
    summary_stats = numeric_data.describe().T[['mean', '50%', 'min', 'max']]
    summary_stats.rename(columns={'50%': 'median'}, inplace=True)

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red

    # boxplots
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=numeric_data, palette='Set2', width=0.5)
    plt.title('Box Plot for Numeric Columns', fontsize=16)
    plt.xlabel('Columns', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{name}/summary_stat.png")

# correlation matrix
def correlation_matrix():
    numeric_data = data.select_dtypes(include=['number'])
    if not numeric_data.empty:
        plt.figure(figsize=(10, 8))
        sns.heatmap(numeric_data.corr(), annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True)
        plt.title('Correlation Matrix')
        plt.savefig(f"{name}/correlation_matrix.png")

    else:
        print("No numeric columns available for correlation matrix.")

def clustering_plot():
    numeric_data = data.select_dtypes(include=['number'])
    if numeric_data.empty:
        print("No numeric columns found for clustering.")
        return

    # Handle missing values by imputing with the mean
    imputer = SimpleImputer(strategy='mean')
    numeric_data_imputed = pd.DataFrame(imputer.fit_transform(numeric_data), columns=numeric_data.columns)

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_data_imputed)

    # K-Means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    cluster_labels = kmeans.fit_predict(scaled_data)

    # Reduce dimensions using PCA for visualization
    pca = PCA(n_components=2)
    pca_data = pca.fit_transform(scaled_data)

    # Scatter plot
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(pca_data[:, 0], pca_data[:, 1], c=cluster_labels, cmap='viridis', alpha=0.7, edgecolor='k')
    plt.title('K-Means Clustering Visualization')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.colorbar(scatter, label='Cluster')
    plt.savefig(f"{name}/clustering_plot.png")
   
def name_file(string: str):
    # Returns the fitered filename without . and \\
        if "\\" in string:
            string = string.split("\\")[1]
        if '.' in string:
            string = string.split(".")[0]
        return string

def create_directory():
    """
    Generates a base directory based on the processed name of the input file.
    
    Parameters:
    file_path (str): The input file path (e.g., 'dataset.csv').

    Returns:
    None: Creates the base directory in the current working directory.
    """

    # Process the file name
    processed_name = name_file(sys.argv[1])
    # Create the base directory
    try:
        os.makedirs(processed_name)
    except:
        pass

def llm_analysis(description):
    proxy_url = 'https://aiproxy.sanand.workers.dev/openai/v1/chat/completions'

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('AIPROXY_TOKEN')}"
    }
    payload = {
        'model': 'gpt-4o-mini',
        "messages": [
            {'role': 'system', 'content':"Analyze the provided dataset comprehensively. Identify key patterns, correlations, and outliers, and provide detailed insights. Highlight significant features, statistical trends, and potential implications for further exploration. Focus on offering a clean, understandable summary that blends statistical rigor with an engaging narrative. Avoid generic conclusions, and aim for unique observations that might inspire further analysis or innovation."},
            {'role': 'user', 'content': f"Data is: {description}"}
        ],
        'temperature': 0,
        'max_tokens': 1000
    }
    
    response = requests.post(url=proxy_url, headers=headers, json=payload)
    if response.ok:
        ai_response = response.json()
        result = ai_response["choices"][0]["message"]["content"].strip()
        
        # Ensure directory exists
        if not os.path.exists(name):
            print(f"Directory {name} does not exist.")
            return
        
        # Write to README.md
        try:
            with open(f"{name}/README.md", "w") as f:
                f.write(result)
        except Exception as e:
            print(f"Error writing README.md: {e}")
    else:
        print(f"Error Fetching the summary. Status code: {response.status_code}")
        print(f"Response content: {response.content}")

load_dotenv()
data = load_data()

name = name_file(sys.argv[1])

create_directory()

summary_statistics_plot()
correlation_matrix()
clustering_plot()

llm_prompt = get_description(data)
llm_analysis(llm_prompt)

print("****************************** Autolysis Completed ******************************")
