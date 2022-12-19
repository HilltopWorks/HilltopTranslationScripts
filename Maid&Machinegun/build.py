import Font
import script
import dataDuplication
import TEX



print("Building and injecting font...")
Font.injectFont(Font.buildFont(), "INSTANCE/MAP_0x17b6800_0x17f6840.modified")

print("Injecting MMDH scripts...")
script.injectMMDHs()
print("Injecting EXE pointer scripts...")
script.injectMaidScripts()
print("Injecting EXE HI/LO scripts...")
script.injectLoadScripts()
print("Injecting MYU0 script...")
script.injectMYU0Segment(script.MAID_RAW_SCRIPTS[0], script.RAW_MODE)
print("Injecting EXE fragments...")
script.editMaidFragments(script.MAID_FRAGMENTS)

print("Injecting GFX...")
TEX.repack()

#Images

print("Propagating modified files...")
dataDuplication.propagateFiles()

