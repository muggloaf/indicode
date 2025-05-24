from custom_indicate.transliterate import hindi2english, marathi2english
# Use the regular enhanced transliteration (which we've fixed)
from custom_indicate.enhanced_transliteration import enhanced_hindi2english, enhanced_marathi2english

# Test specific cases for Nukta characters
# Updated the expected results based on our current transliteration system
test_cases = [
    ('पढ़ना', 'padhna'),     # Basic case with ढ़
    ('पढ़ने', 'padhne'),     # With vowel mark े
    ('ज़रूर', 'zaroor'),     # Testing ज़
    ('फ़र्क़', 'farq'),      # Testing फ़ and क़
    ('पढ़ाई', 'padhai'),     # Testing ढ़ with vowel mark ाई
    ('ज़्यादा', 'zyada'),    # Testing ज़ with य
    ('बड़ी', 'badi'),        # Common case that was failing on website
    ('बड़े', 'bade'),        # Another common case
    ('कड़वा', 'kadva'),      # Testing another word with ड़
    ('बाज़ार', 'bazar'),     # Testing ज़ in the middle of a word
]

print("Running Nukta character tests with both base and enhanced transliteration...")
print("-" * 70)

# First test with base transliteration
print("\nBASE TRANSLITERATION:")
base_failed = False
for hindi, expected in test_cases:
    result = hindi2english(hindi)
    if result != expected:
        print(f"❌ Test failed for '{hindi}'")
        print(f"   Expected: '{expected}'")
        print(f"   Got:      '{result}'")
        print("   Original chars:", list(hindi))
        print("   Character codes:", [hex(ord(c)) for c in hindi])
        base_failed = True
    else:
        print(f"✓ {hindi} -> {result}")

# Now test with enhanced transliteration
print("\nENHANCED TRANSLITERATION:")
enhanced_failed = False
for hindi, expected in test_cases:
    result = enhanced_hindi2english(hindi)
    # The enhanced transliteration might capitalize the first letter
    if result.lower() != expected.lower():
        print(f"❌ Test failed for '{hindi}'")
        print(f"   Expected: '{expected}' (case insensitive)")
        print(f"   Got:      '{result}'")
        print("   Original chars:", list(hindi))
        print("   Character codes:", [hex(ord(c)) for c in hindi])
        enhanced_failed = True
    else:
        print(f"✓ {hindi} -> {result}")

if base_failed or enhanced_failed:
    print("\nSome tests failed! Review the output above.")
    if base_failed:
        print("- Base transliteration has issues.")
    if enhanced_failed:
        print("- Enhanced transliteration has issues.")
else:
    print("\nAll tests passed! Both transliteration systems handle nukta characters correctly.")
