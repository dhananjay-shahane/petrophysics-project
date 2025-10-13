
import os

def generate_ressum_list_from_geolog_report(sourcefolder, sourcefile, dataset_name):
    file_path = os.path.join(sourcefolder, sourcefile)
    file_lines = []

    try:
        # Check if the file exists
        if file_path:
            with open(file_path, 'r') as file:
                for file_line in file:
                    if file_line.strip():  # Ignore empty or whitespace-only lines
                        file_lines.append(file_line.lstrip())  # Add the line, stripping leading spaces
    except Exception as e:
        print(f"Error reading the file: {e}")
    
    # Optionally, process the lines further here...
    return file_lines

def res_list_from_paysense(lines, dataset_name):
    data_section = 0
    data_row = 0
    _well = ""
    _interval = ""
    _top = 0.0
    _bottom = 0.0

    ressum_list = []
    for line in lines:
        lst = line.split()
        if not lst:
            continue
        
        first_item = lst[0].strip()

        if first_item == "Well:":
            data_section += 1
            _well = lst[1].strip()
        
        elif first_item == "Interval:":
            _interval = ""
            for txt in lst:
                _interval += " " + txt.strip()
            _interval = _interval.strip()
            _interval = _interval.split(' ', 1)[-1]
        
        elif first_item == "Process":
            _top = float(lst[2].strip().rstrip('!'))
            _bottom = float(lst[4].strip())
        
        else:
            try:
                # Check if the first element is a number (similar to double.TryParse in C#)
                value = float(lst[0].strip())
                if 0 <= value < 1:
                    data_row += 1
                    ressum_list.append(RESSUM(
                        well=_well,
                        interval=_interval,
                        top=_top,
                        bottom=_bottom,
                        gross=_bottom - _top,
                        phiec=float(lst[0].strip()),
                        swec=float(lst[1].strip()),
                        vshc=float(lst[2].strip()),
                        phie=float(lst[3].strip()),
                        swe=float(lst[4].strip()),
                        vsh=float(lst[5].strip()),
                        phih=float(lst[6].strip()),
                        sophih=float(lst[7].strip()),
                        netpay=float(lst[8].strip()),
                        ntg=float(lst[8].strip()) / (_bottom - _top),
                        dataset=dataset_name,
                        reference="TVDSS"
                    ))
            except ValueError:
                # Handle the case when the value cannot be converted to float
                continue
    
    return ressum_list