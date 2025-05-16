from custom_indicate import enhanced_hindi2english

try:
    result = enhanced_hindi2english('नमस्ते')
    print(f"Transliteration result: {result}")
except Exception as e:
    print(f"Error occurred: {str(e)}")
    import traceback
    traceback.print_exc()

print("Script completed")
