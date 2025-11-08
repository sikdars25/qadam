#!/usr/bin/env python3
"""
Complete LaTeX-OCR + Post-processing Pipeline Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latex_postprocessor import post_process_latex_ocr_result
import logging

def test_latex_pipeline():
    """Test the complete LaTeX-OCR processing pipeline"""
    
    print("🧮 Complete LaTeX-OCR Pipeline Test")
    print("=" * 60)
    
    # Test with the actual LaTeX output you provided
    test_latex_output = r"\begin{array}{l l l l}{{(\mathbf{a})}}&{{\mathrm{Define~}^{\mathrm{tonsity}, ~f s~i t~a~e c a l a r~o r~a~v e c t o r~};~{\mathrm{kn~electric~fteld}}}}\\ {{}}&{{\mathrm{E}~\mathrm{is~~maintianed~in~onetor~in~orathe~conductior~in}~~}}\\ {{}}&{{\mathrm{electrons~(maxs~m, ~chare}~\mathrm{plar~the~conducter}~i n}}}\\ {{}}&{{\mathrm{and~riar~time}~\mathrm{the~curent~un~the~conducte}}}\\ {{}}&{{\mathrm{where}~\mathrm{trin}~~}}&{{\mathrm{~~}}}\end{array}"
    
    print("📝 Input LaTeX from LaTeX-OCR:")
    print(test_latex_output[:200] + "...")
    
    # Step 1: Post-process the LaTeX output
    print(f"\n🔧 Step 1: LaTeX Post-processing")
    print("-" * 35)
    
    processed_result = post_process_latex_ocr_result(test_latex_output)
    
    print(f"✅ Cleaned LaTeX: {processed_result['cleaned_latex'][:150]}...")
    print(f"📄 Extracted Text: {processed_result['extracted_text']}")
    print(f"🔧 Corrected Text: {processed_result['corrected_text']}")
    print(f"📊 Corrections Applied: {processed_result['corrections_applied']}")
    
    # Step 2: Analyze improvements
    print(f"\n📈 Step 2: Analysis of Improvements")
    print("-" * 40)
    
    improvements = []
    
    # Check for word corrections
    original_words = test_latex_output.split()
    corrected_words = processed_result['extracted_text'].split()
    
    word_fixes = [
        'tonsity → density',
        'maintianed → maintained', 
        'maxs → mass',
        'chare → charge',
        'conducter → conductor',
        'curent → current',
        'fteld → field'
    ]
    
    for fix in word_fixes:
        old_word, new_word = fix.split(' → ')
        if old_word in test_latex_output and new_word in processed_result['extracted_text']:
            improvements.append(fix)
    
    if improvements:
        print("✅ Word Corrections Detected:")
        for improvement in improvements:
            print(f"  • {improvement}")
    
    # Check for LaTeX structure preservation
    if r'\begin{array}' in processed_result['cleaned_latex']:
        improvements.append("LaTeX structure preserved")
    
    if r'\mathrm{' in processed_result['cleaned_latex']:
        improvements.append("Mathematical formatting preserved")
    
    # Step 3: Expected final output
    print(f"\n🎯 Step 3: Expected Final Output")
    print("-" * 35)
    
    expected_text = "(a) Define density, is it a scalar or a vector; in electric field E is maintained in one or in other conductor in electrons (mass m, charge play the conductor in and via time the current in the conductor where thin"
    
    print("📝 Expected readable text:")
    print(expected_text)
    
    print(f"\n📝 Actual corrected text:")
    print(processed_result['corrected_text'])
    
    # Step 4: Quality assessment
    print(f"\n📊 Step 4: Quality Assessment")
    print("-" * 30)
    
    quality_score = 0
    max_score = 5
    
    # LaTeX structure preserved
    if r'\begin{array}' in processed_result['cleaned_latex']:
        quality_score += 1
        print("✅ LaTeX structure preserved")
    
    # Word corrections applied
    if len(improvements) > 3:
        quality_score += 1
        print(f"✅ Multiple word corrections applied ({len(improvements)})")
    
    # Mathematical content detected
    if any(word in processed_result['extracted_text'].lower() for word in ['density', 'electric', 'field', 'electrons', 'current']):
        quality_score += 1
        print("✅ Mathematical content preserved")
    
    # Readable text extracted
    if len(processed_result['extracted_text']) > 50:
        quality_score += 1
        print("✅ Readable text extracted")
    
    # Generic symbol corrections applied
    if processed_result['corrected_text'] != processed_result['extracted_text']:
        quality_score += 1
        print("✅ Generic symbol corrections applied")
    
    print(f"\n🎯 Overall Quality Score: {quality_score}/{max_score}")
    
    if quality_score >= 4:
        print("🎉 EXCELLENT: LaTeX-OCR pipeline is working very well!")
        print("✅ Mathematical expressions detected and processed")
        print("✅ OCR errors corrected intelligently")
        print("✅ LaTeX structure maintained")
        print("✅ Readable output generated")
    elif quality_score >= 3:
        print("✅ GOOD: LaTeX-OCR pipeline is working well")
        print("⚠️ Some improvements may be needed")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Pipeline needs refinement")
    
    return quality_score >= 3

def test_pipeline_integration():
    """Test integration with the main OCR system"""
    
    print(f"\n🔗 Step 5: Pipeline Integration Test")
    print("-" * 40)
    
    try:
        # Test importing the main components
        from app import correct_math_symbols
        from latex_postprocessor import post_process_latex_ocr_result
        
        print("✅ All components imported successfully")
        
        # Test a mathematical expression
        test_math = "current density j = a E ne^2 where Q = 3 m"
        corrected = correct_math_symbols(test_math)
        
        print(f"📝 Generic system test:")
        print(f"  Input: {test_math}")
        print(f"  Output: {corrected}")
        
        if corrected != test_math:
            print("✅ Generic symbol corrections working")
            return True
        else:
            print("⚠️ Generic symbol corrections not applied")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Complete LaTeX-OCR + Post-processing Pipeline")
    print("=" * 70)
    print("Testing the entire mathematical expression detection system")
    print("=" * 70)
    
    # Test the pipeline
    pipeline_works = test_latex_pipeline()
    integration_works = test_pipeline_integration()
    
    print(f"\n{'='*70}")
    print("📊 FINAL PIPELINE RESULTS:")
    print(f"✅ LaTeX Pipeline: {'PASS' if pipeline_works else 'FAIL'}")
    print(f"✅ Integration: {'PASS' if integration_works else 'FAIL'}")
    
    if pipeline_works and integration_works:
        print("\n🎉 COMPLETE SYSTEM READY!")
        print("🧮 LaTeX-OCR will provide superior mathematical expression detection!")
        print("🔧 Post-processing will clean up OCR errors intelligently!")
        print("✨ Generic system will handle infinite symbol combinations!")
    else:
        print("\n⚠️ Some components need attention")
    
    print(f"\n📋 System Benefits:")
    print("  • LaTeX-OCR: Superior mathematical expression detection")
    print("  • Post-processing: Intelligent OCR error correction")
    print("  • Generic system: No hard-coded patterns needed")
    print("  • Fallback: EasyOCR for non-mathematical content")
    print("  • Complete pipeline: End-to-end mathematical OCR solution")
