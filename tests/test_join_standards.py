from thinkcerca_tool.modules.join_standards import join_module_standards

if __name__ == "__main__":
    try:
        df = join_module_standards()
        print("✅ Joined standards successfully!\n")
        print(df.head(10).to_string())
        print(f"\nTotal joined rows: {len(df)}")
    except Exception as e:
        print("❌ Error joining standards:", e)
