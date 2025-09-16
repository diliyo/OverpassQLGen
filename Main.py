import CodeGenerator

def main():

    print("Overpass Turbo Query Generator:\n\n")
    area_name=input("Enter an area name (eg, Mississauga, Ontario): ").strip()
    print("\nSelect building types separated by commas,\nExample: apartment,office,industrial,retail")
    buildings=input("Enter: ").strip()
    buildings_list=[]
    for building in buildings.split(","):
        if building.strip():
            buildings_list.append(building.strip())

    print("\nEnter colors for each building types in the same order separated by commas, ")
    print("Example: green,cyan,orange,blue")
    colors=input("Enter: ").strip()
    colors_list=[]
    for color in colors.split(","):
        if color.strip():
            colors_list.append(color.strip())

    cg=CodeGenerator()
    color_code=cg.generate_color_code(buildings_list, colors_list)

    print("Generated Overpass QL Code:\n\n")

    overpass_code=cg.generate_overpass_code(area_name, buildings_list, color_code)
    print(overpass_code)
    open_confirmation=input("\nOpen code in Overpass Turbo? (Y/N): ")
    if open_confirmation=='Y':
        cg.open_overpass_turbo(overpass_code)
