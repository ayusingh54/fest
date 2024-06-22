# app.py
from flask import Flask, request, jsonify, send_file
import pandas as pd
import os

app = Flask(__name__)

allocation_results = []

@app.route('/api/allocate', methods=['POST'])
def allocate_rooms():
    global allocation_results
    group_file = request.files['groupFile']
    hostel_file = request.files['hostelFile']
    
    groups_df = pd.read_csv(group_file)
    hostels_df = pd.read_csv(hostel_file)
    
    allocation_results = allocate(groups_df, hostels_df)
    
    return jsonify(allocation_results)

@app.route('/api/download', methods=['GET'])
def download_results():
    global allocation_results
    df = pd.DataFrame(allocation_results)
    df.to_csv('allocation_results.csv', index=False)
    return send_file('allocation_results.csv', as_attachment=True)

def allocate(groups_df, hostels_df):
    allocations = []
    hostels = hostels_df.to_dict('records')
    
    for _, group in groups_df.iterrows():
        group_id = group['Group ID']
        members = group['Members']
        gender = group['Gender']
        allocated = False
        
        for hostel in hostels:
            if hostel['Gender'] == gender and hostel['Capacity'] >= members:
                allocations.append({
                    'Group ID': group_id,
                    'Hostel Name': hostel['Hostel Name'],
                    'Room Number': hostel['Room Number'],
                    'Members Allocated': members
                })
                hostel['Capacity'] -= members
                allocated = True
                break
        
        if not allocated:
            allocations.append({
                'Group ID': group_id,
                'Hostel Name': 'Not Allocated',
                'Room Number': 'Not Allocated',
                'Members Allocated': members
            })
    
    return allocations

if __name__ == '__main__':
    app.run(debug=True)
