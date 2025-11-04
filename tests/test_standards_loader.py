from thinkcerca_tool.modules.standards_loader import load_reference_1, extract_standards

if __name__ == "__main__":
    try:
        sheets = load_reference_1()
        df = extract_standards(sheets)
        print("✅ Standards extracted successfully!")
        print(df.head(10))
        print(f"\nTotal standards found: {len(df)}")
    except Exception as e:
        print("❌ Error:", e)
