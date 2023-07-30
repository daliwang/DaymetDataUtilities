import os 

input_path= '/Users/7xw/Downloads/data_GM/PKG - GM Al-Steel RSW Data 10/GM Al Steel RSW Data 10/'
#input_path = os.getcwd()
print(input_path)
files = os.listdir(input_path) 

files.sort() 
output_path = '/Users/7xw/Downloads/data_GM/Coach_peel/'
file_no =0
df = pd.DataFrame() 
#files_xls= ['C104-1 NO BAKE CP ZrCu018A ZnNi STAND 2.xlsx', 'C105-1 NO BAKE CP ZrCu018A GA-STAND 2.xlsx'] 

files_xls = [f for f in files if (f[-4:] == 'xlsx' and f[0] != '~')] 
print("total " + str(len(files_xls)) + " files need to be processed")

for f in files_xls: 
    print(f)
    ff=input_path + f
    data1 = pd.read_excel(ff, 'Coach peel',usecols= "A:B", skiprows=0, nrows=21, header=None) 
    data2 = pd.read_excel(ff, 'Coach peel',usecols= "D", skiprows=0, nrows=2, header=None) 
    df = df.append(data1)
    # data = pd.concat([data1,data2], axis=1, ignore_index=True) 
    df = df.append(data2.shift(0,axis="columns"))
    file_no += 1
    
file_name = output_path +'condition_schedule_10.csv'
print("total " + str(file_no) + " files processed, and results are saving to " + file_name)
df.to_csv(file_name, index=False)
