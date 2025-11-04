from thinkcerca_tool.modules.standards_descriptions import load_standard_descriptions

if __name__ == "__main__":
    try:
        df = load_standard_descriptions()
        print("✅ Standards descriptions loaded successfully!")
        print(df.head(10).to_string())
        print(f"\nTotal unique standards found: {len(df)}")
    except Exception as e:
        print("❌ Error loading standards descriptions:", e)
