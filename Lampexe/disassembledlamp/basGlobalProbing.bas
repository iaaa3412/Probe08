
Private Function Proc_2_0_41CA40(arg_C, arg_10, arg_14) '41CA40
  loc_0041CA40: push ebp
  loc_0041CA41: mov ebp, esp
  loc_0041CA43: sub esp, 00000018h
  loc_0041CA46: push 00401AA6h ; __vbaExceptHandler
  loc_0041CA4B: mov eax, fs:[00000000h]
  loc_0041CA51: push eax
  loc_0041CA52: mov fs:[00000000h], esp
  loc_0041CA59: mov eax, 00000184h
  loc_0041CA5E: call 00401AA0h ; __vbaChkstk
  loc_0041CA63: push ebx
  loc_0041CA64: push esi
  loc_0041CA65: push edi
  loc_0041CA66: mov var_18, esp
  loc_0041CA69: mov var_14, 004016D0h ; "."
  loc_0041CA70: mov var_10, 00000000h
  loc_0041CA77: mov var_C, 00000000h
  loc_0041CA7E: mov var_4, 00000001h
  loc_0041CA85: mov var_4, 00000002h
  loc_0041CA8C: mov eax, arg_14
  loc_0041CA8F: push eax
  loc_0041CA90: call [0040106Ch] ; rtcIsMissing
  loc_0041CA96: movsx ecx, ax
  loc_0041CA99: test ecx, ecx
  loc_0041CA9B: jnz 0041CAFAh
  loc_0041CA9D: mov var_4, 00000003h
  loc_0041CAA4: mov var_CC, FFFFFFFFh
  loc_0041CAAE: mov var_D4, 0000800Bh
  loc_0041CAB8: mov edx, arg_14
  loc_0041CABB: lea ecx, var_E4
  loc_0041CAC1: call [0040101Ch] ; __vbaVarVargNofree
  loc_0041CAC7: push eax
  loc_0041CAC8: lea edx, var_D4
  loc_0041CACE: push edx
  loc_0041CACF: call [004010E4h] ; __vbaVarTstEq
  loc_0041CAD5: movsx eax, ax
  loc_0041CAD8: test eax, eax
  loc_0041CADA: jz 0041CAEBh
  loc_0041CADC: mov var_4, 00000004h
  loc_0041CAE3: mov var_30, FFFFFFh
  loc_0041CAE9: jmp 0041CAF8h
  loc_0041CAEB: mov var_4, 00000006h
  loc_0041CAF2: mov var_30, 0000h
  loc_0041CAF8: jmp 0041CB07h
  loc_0041CAFA: mov var_4, 00000009h
  loc_0041CB01: mov var_30, 0000h
  loc_0041CB07: mov var_4, 0000000Bh
  loc_0041CB0E: push 00000001h
  loc_0041CB10: mov ecx, arg_10
  loc_0041CB13: mov edx, [ecx]
  loc_0041CB15: push edx
  loc_0041CB16: push 00407D54h
  loc_0041CB1B: push 00000000h
  loc_0041CB1D: call [0040116Ch] ; __vbaInStr
  loc_0041CB23: test eax, eax
  loc_0041CB25: jle 0041CB34h
  loc_0041CB27: mov var_4, 0000000Ch
  loc_0041CB2E: mov var_30, FFFFFFh
  loc_0041CB34: mov var_4, 0000000Eh
  loc_0041CB3B: push 004074F0h ; "HPIB_"
  loc_0041CB40: mov eax, arg_C
  loc_0041CB43: mov ecx, [eax]
  loc_0041CB45: push ecx
  loc_0041CB46: call [00401050h] ; __vbaStrCat
  loc_0041CB4C: mov edx, eax
  loc_0041CB4E: lea ecx, var_58
  loc_0041CB51: call [004011D0h] ; __vbaStrMove
  loc_0041CB57: mov var_4, 0000000Fh
  loc_0041CB5E: lea edx, var_58
  loc_0041CB61: mov var_CC, edx
  loc_0041CB67: mov var_D4, 00004008h
  loc_0041CB71: cmp [00423054h], 00000000h
  loc_0041CB78: jnz 0041CB96h
  loc_0041CB7A: push 00423054h
  loc_0041CB7F: push 004033BCh
  loc_0041CB84: call [00401168h] ; __vbaNew2
  loc_0041CB8A: mov var_188, 00423054h
  loc_0041CB94: jmp 0041CBA0h
  loc_0041CB96: mov var_188, 00423054h
  loc_0041CBA0: mov eax, var_188
  loc_0041CBA6: mov ecx, [eax]
  loc_0041CBA8: mov var_150, ecx
  loc_0041CBAE: lea edx, var_80
  loc_0041CBB1: push edx
  loc_0041CBB2: mov eax, var_150
  loc_0041CBB8: mov ecx, [eax]
  loc_0041CBBA: mov edx, var_150
  loc_0041CBC0: push edx
  loc_0041CBC1: call [ecx+00000218h]
  loc_0041CBC7: fnclex
  loc_0041CBC9: mov var_154, eax
  loc_0041CBCF: cmp var_154, 00000000h
  loc_0041CBD6: jge 0041CBFEh
  loc_0041CBD8: push 00000218h
  loc_0041CBDD: push 0040576Ch
  loc_0041CBE2: mov eax, var_150
  loc_0041CBE8: push eax
  loc_0041CBE9: mov ecx, var_154
  loc_0041CBEF: push ecx
  loc_0041CBF0: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041CBF6: mov var_18C, eax
  loc_0041CBFC: jmp 0041CC08h
  loc_0041CBFE: mov var_18C, 00000000h
  loc_0041CC08: push 00405B4Ch
  loc_0041CC0D: mov eax, 00000010h
  loc_0041CC12: call 00401AA0h ; __vbaChkstk
  loc_0041CC17: mov edx, esp
  loc_0041CC19: mov eax, var_D4
  loc_0041CC1F: mov [edx], eax
  loc_0041CC21: mov ecx, var_D0
  loc_0041CC27: mov [edx+00000004h], ecx
  loc_0041CC2A: mov eax, var_CC
  loc_0041CC30: mov [edx+00000008h], eax
  loc_0041CC33: mov ecx, var_C8
  loc_0041CC39: mov [edx+0000000Ch], ecx
  loc_0041CC3C: push 00000001h
  loc_0041CC3E: push 00000000h
  loc_0041CC40: mov edx, var_80
  loc_0041CC43: push edx
  loc_0041CC44: lea eax, var_94
  loc_0041CC4A: push eax
  loc_0041CC4B: call [00401100h] ; __vbaLateIdCallLd
  loc_0041CC51: add esp, 00000020h
  loc_0041CC54: push eax
  loc_0041CC55: call [004010F4h] ; __vbaCastObjVar
  loc_0041CC5B: push eax
  loc_0041CC5C: lea ecx, var_28
  loc_0041CC5F: push ecx
  loc_0041CC60: call [00401080h] ; __vbaObjSet
  loc_0041CC66: lea ecx, var_80
  loc_0041CC69: call [004011F0h] ; __vbaFreeObj
  loc_0041CC6F: lea ecx, var_94
  loc_0041CC75: call [00401020h] ; __vbaFreeVar
  loc_0041CC7B: mov var_4, 00000010h
  loc_0041CC82: xor edx, edx
  loc_0041CC84: test edx, edx
  loc_0041CC86: jz 0041CE2Bh
  loc_0041CC8C: mov var_4, 00000011h
  loc_0041CC93: push 00407D5Ch ; "About to Output to "
  loc_0041CC98: mov eax, arg_C
  loc_0041CC9B: mov ecx, [eax]
  loc_0041CC9D: push ecx
  loc_0041CC9E: call [00401050h] ; __vbaStrCat
  loc_0041CCA4: mov edx, eax
  loc_0041CCA6: lea ecx, var_5C
  loc_0041CCA9: call [004011D0h] ; __vbaStrMove
  loc_0041CCAF: push eax
  loc_0041CCB0: push 00407D88h ; " '"
  loc_0041CCB5: call [00401050h] ; __vbaStrCat
  loc_0041CCBB: mov edx, eax
  loc_0041CCBD: lea ecx, var_60
  loc_0041CCC0: call [004011D0h] ; __vbaStrMove
  loc_0041CCC6: push eax
  loc_0041CCC7: mov edx, arg_10
  loc_0041CCCA: mov eax, [edx]
  loc_0041CCCC: push eax
  loc_0041CCCD: call [00401050h] ; __vbaStrCat
  loc_0041CCD3: mov edx, eax
  loc_0041CCD5: lea ecx, var_64
  loc_0041CCD8: call [004011D0h] ; __vbaStrMove
  loc_0041CCDE: push eax
  loc_0041CCDF: push 0040758Ch ; "'"
  loc_0041CCE4: call [00401050h] ; __vbaStrCat
  loc_0041CCEA: mov edx, eax
  loc_0041CCEC: lea ecx, var_68
  loc_0041CCEF: call [004011D0h] ; __vbaStrMove
  loc_0041CCF5: push eax
  loc_0041CCF6: push 004054D8h ; vbCrLf
  loc_0041CCFB: call [00401050h] ; __vbaStrCat
  loc_0041CD01: mov edx, eax
  loc_0041CD03: lea ecx, var_2C
  loc_0041CD06: call [004011D0h] ; __vbaStrMove
  loc_0041CD0C: lea ecx, var_68
  loc_0041CD0F: push ecx
  loc_0041CD10: lea edx, var_64
  loc_0041CD13: push edx
  loc_0041CD14: lea eax, var_60
  loc_0041CD17: push eax
  loc_0041CD18: lea ecx, var_5C
  loc_0041CD1B: push ecx
  loc_0041CD1C: push 00000004h
  loc_0041CD1E: call [00401180h] ; __vbaFreeStrList
  loc_0041CD24: add esp, 00000014h
  loc_0041CD27: mov var_4, 00000012h
  loc_0041CD2E: movsx edx, var_30
  loc_0041CD32: test edx, edx
  loc_0041CD34: jz 0041CD57h
  loc_0041CD36: mov var_4, 00000013h
  loc_0041CD3D: mov eax, var_2C
  loc_0041CD40: push eax
  loc_0041CD41: push 00407D94h ; "Reply Expected"
  loc_0041CD46: call [00401050h] ; __vbaStrCat
  loc_0041CD4C: mov edx, eax
  loc_0041CD4E: lea ecx, var_2C
  loc_0041CD51: call [004011D0h] ; __vbaStrMove
  loc_0041CD57: mov var_4, 00000015h
  loc_0041CD5E: mov var_AC, 80020004h
  loc_0041CD68: mov var_B4, 0000000Ah
  loc_0041CD72: mov var_9C, 80020004h
  loc_0041CD7C: mov var_A4, 0000000Ah
  loc_0041CD86: mov var_DC, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041CD90: mov var_E4, 00000008h
  loc_0041CD9A: lea edx, var_E4
  loc_0041CDA0: lea ecx, var_94
  loc_0041CDA6: call [004011B4h] ; __vbaVarDup
  loc_0041CDAC: lea ecx, var_2C
  loc_0041CDAF: mov var_CC, ecx
  loc_0041CDB5: mov var_D4, 00004008h
  loc_0041CDBF: lea edx, var_B4
  loc_0041CDC5: push edx
  loc_0041CDC6: lea eax, var_A4
  loc_0041CDCC: push eax
  loc_0041CDCD: lea ecx, var_94
  loc_0041CDD3: push ecx
  loc_0041CDD4: push 00000001h
  loc_0041CDD6: lea edx, var_D4
  loc_0041CDDC: push edx
  loc_0041CDDD: call [00401084h] ; rtcMsgBox
  loc_0041CDE3: mov ecx, eax
  loc_0041CDE5: call [004010ECh] ; __vbaI2I4
  loc_0041CDEB: mov var_24, ax
  loc_0041CDEF: lea eax, var_B4
  loc_0041CDF5: push eax
  loc_0041CDF6: lea ecx, var_A4
  loc_0041CDFC: push ecx
  loc_0041CDFD: lea edx, var_94
  loc_0041CE03: push edx
  loc_0041CE04: push 00000003h
  loc_0041CE06: call [00401038h] ; __vbaFreeVarList
  loc_0041CE0C: add esp, 00000010h
  loc_0041CE0F: mov var_4, 00000016h
  loc_0041CE16: movsx eax, var_24
  loc_0041CE1A: cmp eax, 00000002h
  loc_0041CE1D: jnz 0041CE2Bh
  loc_0041CE1F: mov var_4, 00000017h
  loc_0041CE26: call 0041ECE0h
  loc_0041CE2B: mov var_4, 0000001Ah
  loc_0041CE32: xor ecx, ecx
  loc_0041CE34: test ecx, ecx
  loc_0041CE36: jz 0041CE3Dh
  loc_0041CE38: jmp 0041DABAh
  loc_0041CE3D: mov var_4, 0000001Dh
  loc_0041CE44: mov var_34, 00000000h
  loc_0041CE4B: mov var_4, 0000001Eh
  loc_0041CE52: push FFFFFFFFh
  loc_0041CE54: call [0040107Ch] ; __vbaOnError
  loc_0041CE5A: mov var_4, 00000020h
  loc_0041CE61: mov edx, arg_10
  loc_0041CE64: mov var_CC, edx
  loc_0041CE6A: mov var_D4, 00004008h
  loc_0041CE74: mov eax, 00000010h
  loc_0041CE79: call 00401AA0h ; __vbaChkstk
  loc_0041CE7E: mov eax, esp
  loc_0041CE80: mov ecx, var_D4
  loc_0041CE86: mov [eax], ecx
  loc_0041CE88: mov edx, var_D0
  loc_0041CE8E: mov [eax+00000004h], edx
  loc_0041CE91: mov ecx, var_CC
  loc_0041CE97: mov [eax+00000008h], ecx
  loc_0041CE9A: mov edx, var_C8
  loc_0041CEA0: mov [eax+0000000Ch], edx
  loc_0041CEA3: push 00000001h
  loc_0041CEA5: push 00407DB4h ; "Output"
  loc_0041CEAA: mov eax, var_28
  loc_0041CEAD: push eax
  loc_0041CEAE: call [004011A8h] ; __vbaLateMemCall
  loc_0041CEB4: add esp, 0000001Ch
  loc_0041CEB7: mov var_4, 00000021h
  loc_0041CEBE: call [00401190h] ; rtcErrObj
  loc_0041CEC4: push eax
  loc_0041CEC5: lea ecx, var_80
  loc_0041CEC8: push ecx
  loc_0041CEC9: call [00401080h] ; __vbaObjSet
  loc_0041CECF: mov var_150, eax
  loc_0041CED5: lea edx, var_148
  loc_0041CEDB: push edx
  loc_0041CEDC: mov eax, var_150
  loc_0041CEE2: mov ecx, [eax]
  loc_0041CEE4: mov edx, var_150
  loc_0041CEEA: push edx
  loc_0041CEEB: call [ecx+0000001Ch]
  loc_0041CEEE: fnclex
  loc_0041CEF0: mov var_154, eax
  loc_0041CEF6: cmp var_154, 00000000h
  loc_0041CEFD: jge 0041CF22h
  loc_0041CEFF: push 0000001Ch
  loc_0041CF01: push 00406F64h
  loc_0041CF06: mov eax, var_150
  loc_0041CF0C: push eax
  loc_0041CF0D: mov ecx, var_154
  loc_0041CF13: push ecx
  loc_0041CF14: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041CF1A: mov var_190, eax
  loc_0041CF20: jmp 0041CF2Ch
  loc_0041CF22: mov var_190, 00000000h
  loc_0041CF2C: xor edx, edx
  loc_0041CF2E: cmp var_148, 00000000h
  loc_0041CF35: setnz dl
  loc_0041CF38: neg edx
  loc_0041CF3A: mov var_158, dx
  loc_0041CF41: lea ecx, var_80
  loc_0041CF44: call [004011F0h] ; __vbaFreeObj
  loc_0041CF4A: movsx eax, var_158
  loc_0041CF51: test eax, eax
  loc_0041CF53: jz 0041D3C7h
  loc_0041CF59: mov var_4, 00000022h
  loc_0041CF60: call [00401190h] ; rtcErrObj
  loc_0041CF66: push eax
  loc_0041CF67: lea ecx, var_80
  loc_0041CF6A: push ecx
  loc_0041CF6B: call [00401080h] ; __vbaObjSet
  loc_0041CF71: mov var_150, eax
  loc_0041CF77: lea edx, var_5C
  loc_0041CF7A: push edx
  loc_0041CF7B: mov eax, var_150
  loc_0041CF81: mov ecx, [eax]
  loc_0041CF83: mov edx, var_150
  loc_0041CF89: push edx
  loc_0041CF8A: call [ecx+0000002Ch]
  loc_0041CF8D: fnclex
  loc_0041CF8F: mov var_154, eax
  loc_0041CF95: cmp var_154, 00000000h
  loc_0041CF9C: jge 0041CFC1h
  loc_0041CF9E: push 0000002Ch
  loc_0041CFA0: push 00406F64h
  loc_0041CFA5: mov eax, var_150
  loc_0041CFAB: push eax
  loc_0041CFAC: mov ecx, var_154
  loc_0041CFB2: push ecx
  loc_0041CFB3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041CFB9: mov var_194, eax
  loc_0041CFBF: jmp 0041CFCBh
  loc_0041CFC1: mov var_194, 00000000h
  loc_0041CFCB: call [00401190h] ; rtcErrObj
  loc_0041CFD1: push eax
  loc_0041CFD2: lea edx, var_84
  loc_0041CFD8: push edx
  loc_0041CFD9: call [00401080h] ; __vbaObjSet
  loc_0041CFDF: mov var_158, eax
  loc_0041CFE5: lea eax, var_148
  loc_0041CFEB: push eax
  loc_0041CFEC: mov ecx, var_158
  loc_0041CFF2: mov edx, [ecx]
  loc_0041CFF4: mov eax, var_158
  loc_0041CFFA: push eax
  loc_0041CFFB: call [edx+0000001Ch]
  loc_0041CFFE: fnclex
  loc_0041D000: mov var_15C, eax
  loc_0041D006: cmp var_15C, 00000000h
  loc_0041D00D: jge 0041D032h
  loc_0041D00F: push 0000001Ch
  loc_0041D011: push 00406F64h
  loc_0041D016: mov ecx, var_158
  loc_0041D01C: push ecx
  loc_0041D01D: mov edx, var_15C
  loc_0041D023: push edx
  loc_0041D024: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041D02A: mov var_198, eax
  loc_0041D030: jmp 0041D03Ch
  loc_0041D032: mov var_198, 00000000h
  loc_0041D03C: mov eax, var_148
  loc_0041D042: mov var_14C, eax
  loc_0041D048: mov ecx, var_5C
  loc_0041D04B: mov var_184, ecx
  loc_0041D051: mov var_5C, 00000000h
  loc_0041D058: mov edx, var_184
  loc_0041D05E: lea ecx, var_60
  loc_0041D061: call [004011D0h] ; __vbaStrMove
  loc_0041D067: lea edx, var_14C
  loc_0041D06D: push edx
  loc_0041D06E: lea eax, var_60
  loc_0041D071: push eax
  loc_0041D072: mov ecx, arg_10
  loc_0041D075: push ecx
  loc_0041D076: mov edx, arg_C
  loc_0041D079: push edx
  loc_0041D07A: lea eax, var_94
  loc_0041D080: push eax
  loc_0041D081: call 0041E400h
  loc_0041D086: lea ecx, var_60
  loc_0041D089: call [004011F4h] ; __vbaFreeStr
  loc_0041D08F: lea ecx, var_84
  loc_0041D095: push ecx
  loc_0041D096: lea edx, var_80
  loc_0041D099: push edx
  loc_0041D09A: push 00000002h
  loc_0041D09C: call [00401040h] ; __vbaFreeObjList
  loc_0041D0A2: add esp, 0000000Ch
  loc_0041D0A5: lea ecx, var_94
  loc_0041D0AB: call [00401020h] ; __vbaFreeVar
  loc_0041D0B1: mov var_4, 00000023h
  loc_0041D0B8: mov eax, var_34
  loc_0041D0BB: add eax, 00000001h
  loc_0041D0BE: jo 0041DBA5h
  loc_0041D0C4: mov var_34, eax
  loc_0041D0C7: mov var_4, 00000024h
  loc_0041D0CE: cmp var_34, 00000005h
  loc_0041D0D2: jge 0041D117h
  loc_0041D0D4: mov var_4, 00000025h
  loc_0041D0DB: call [00401190h] ; rtcErrObj
  loc_0041D0E1: push eax
  loc_0041D0E2: lea ecx, var_80
  loc_0041D0E5: push ecx
  loc_0041D0E6: call [00401080h] ; __vbaObjSet
  loc_0041D0EC: mov var_19C, eax
  loc_0041D0F2: mov edx, var_19C
  loc_0041D0F8: mov eax, [edx]
  loc_0041D0FA: mov ecx, var_19C
  loc_0041D100: push ecx
  loc_0041D101: call [eax+00000048h]
  loc_0041D104: lea ecx, var_80
  loc_0041D107: call [004011F0h] ; __vbaFreeObj
  loc_0041D10D: jmp 0041CE5Ah
  loc_0041D112: jmp 0041D3C7h
  loc_0041D117: mov var_4, 00000028h
  loc_0041D11E: call [00401190h] ; rtcErrObj
  loc_0041D124: push eax
  loc_0041D125: lea edx, var_80
  loc_0041D128: push edx
  loc_0041D129: call [00401080h] ; __vbaObjSet
  loc_0041D12F: mov var_150, eax
  loc_0041D135: lea eax, var_148
  loc_0041D13B: push eax
  loc_0041D13C: mov ecx, var_150
  loc_0041D142: mov edx, [ecx]
  loc_0041D144: mov eax, var_150
  loc_0041D14A: push eax
  loc_0041D14B: call [edx+0000001Ch]
  loc_0041D14E: fnclex
  loc_0041D150: mov var_154, eax
  loc_0041D156: cmp var_154, 00000000h
  loc_0041D15D: jge 0041D182h
  loc_0041D15F: push 0000001Ch
  loc_0041D161: push 00406F64h
  loc_0041D166: mov ecx, var_150
  loc_0041D16C: push ecx
  loc_0041D16D: mov edx, var_154
  loc_0041D173: push edx
  loc_0041D174: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041D17A: mov var_1A0, eax
  loc_0041D180: jmp 0041D18Ch
  loc_0041D182: mov var_1A0, 00000000h
  loc_0041D18C: call [00401190h] ; rtcErrObj
  loc_0041D192: push eax
  loc_0041D193: lea eax, var_84
  loc_0041D199: push eax
  loc_0041D19A: call [00401080h] ; __vbaObjSet
  loc_0041D1A0: mov var_158, eax
  loc_0041D1A6: lea ecx, var_74
  loc_0041D1A9: push ecx
  loc_0041D1AA: mov edx, var_158
  loc_0041D1B0: mov eax, [edx]
  loc_0041D1B2: mov ecx, var_158
  loc_0041D1B8: push ecx
  loc_0041D1B9: call [eax+0000002Ch]
  loc_0041D1BC: fnclex
  loc_0041D1BE: mov var_15C, eax
  loc_0041D1C4: cmp var_15C, 00000000h
  loc_0041D1CB: jge 0041D1F0h
  loc_0041D1CD: push 0000002Ch
  loc_0041D1CF: push 00406F64h
  loc_0041D1D4: mov edx, var_158
  loc_0041D1DA: push edx
  loc_0041D1DB: mov eax, var_15C
  loc_0041D1E1: push eax
  loc_0041D1E2: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041D1E8: mov var_1A4, eax
  loc_0041D1EE: jmp 0041D1FAh
  loc_0041D1F0: mov var_1A4, 00000000h
  loc_0041D1FA: mov var_BC, 80020004h
  loc_0041D204: mov var_C4, 0000000Ah
  loc_0041D20E: mov var_AC, 80020004h
  loc_0041D218: mov var_B4, 0000000Ah
  loc_0041D222: mov var_CC, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041D22C: mov var_D4, 00000008h
  loc_0041D236: lea edx, var_D4
  loc_0041D23C: lea ecx, var_A4
  loc_0041D242: call [004011B4h] ; __vbaVarDup
  loc_0041D248: push 00407DD8h ; "Fatal Error: Tried 5 times to send command '"
  loc_0041D24D: mov ecx, arg_10
  loc_0041D250: mov edx, [ecx]
  loc_0041D252: push edx
  loc_0041D253: call [00401050h] ; __vbaStrCat
  loc_0041D259: mov edx, eax
  loc_0041D25B: lea ecx, var_5C
  loc_0041D25E: call [004011D0h] ; __vbaStrMove
  loc_0041D264: push eax
  loc_0041D265: push 00407E38h ; "' to "
  loc_0041D26A: call [00401050h] ; __vbaStrCat
  loc_0041D270: mov edx, eax
  loc_0041D272: lea ecx, var_60
  loc_0041D275: call [004011D0h] ; __vbaStrMove
  loc_0041D27B: push eax
  loc_0041D27C: mov eax, arg_C
  loc_0041D27F: mov ecx, [eax]
  loc_0041D281: push ecx
  loc_0041D282: call [00401050h] ; __vbaStrCat
  loc_0041D288: mov edx, eax
  loc_0041D28A: lea ecx, var_64
  loc_0041D28D: call [004011D0h] ; __vbaStrMove
  loc_0041D293: push eax
  loc_0041D294: push 004054D8h ; vbCrLf
  loc_0041D299: call [00401050h] ; __vbaStrCat
  loc_0041D29F: mov edx, eax
  loc_0041D2A1: lea ecx, var_68
  loc_0041D2A4: call [004011D0h] ; __vbaStrMove
  loc_0041D2AA: push eax
  loc_0041D2AB: mov edx, var_148
  loc_0041D2B1: push edx
  loc_0041D2B2: call [00401018h] ; __vbaStrI4
  loc_0041D2B8: mov edx, eax
  loc_0041D2BA: lea ecx, var_6C
  loc_0041D2BD: call [004011D0h] ; __vbaStrMove
  loc_0041D2C3: push eax
  loc_0041D2C4: call [00401050h] ; __vbaStrCat
  loc_0041D2CA: mov edx, eax
  loc_0041D2CC: lea ecx, var_70
  loc_0041D2CF: call [004011D0h] ; __vbaStrMove
  loc_0041D2D5: push eax
  loc_0041D2D6: push 00407448h
  loc_0041D2DB: call [00401050h] ; __vbaStrCat
  loc_0041D2E1: mov edx, eax
  loc_0041D2E3: lea ecx, var_78
  loc_0041D2E6: call [004011D0h] ; __vbaStrMove
  loc_0041D2EC: push eax
  loc_0041D2ED: mov eax, var_74
  loc_0041D2F0: push eax
  loc_0041D2F1: call [00401050h] ; __vbaStrCat
  loc_0041D2F7: mov edx, eax
  loc_0041D2F9: lea ecx, var_7C
  loc_0041D2FC: call [004011D0h] ; __vbaStrMove
  loc_0041D302: push eax
  loc_0041D303: push 00407E48h ; ". PROGRAM ENDING."
  loc_0041D308: call [00401050h] ; __vbaStrCat
  loc_0041D30E: mov var_8C, eax
  loc_0041D314: mov var_94, 00000008h
  loc_0041D31E: lea ecx, var_C4
  loc_0041D324: push ecx
  loc_0041D325: lea edx, var_B4
  loc_0041D32B: push edx
  loc_0041D32C: lea eax, var_A4
  loc_0041D332: push eax
  loc_0041D333: push 00000010h
  loc_0041D335: lea ecx, var_94
  loc_0041D33B: push ecx
  loc_0041D33C: call [00401084h] ; rtcMsgBox
  loc_0041D342: lea edx, var_7C
  loc_0041D345: push edx
  loc_0041D346: lea eax, var_74
  loc_0041D349: push eax
  loc_0041D34A: lea ecx, var_78
  loc_0041D34D: push ecx
  loc_0041D34E: lea edx, var_70
  loc_0041D351: push edx
  loc_0041D352: lea eax, var_6C
  loc_0041D355: push eax
  loc_0041D356: lea ecx, var_68
  loc_0041D359: push ecx
  loc_0041D35A: lea edx, var_64
  loc_0041D35D: push edx
  loc_0041D35E: lea eax, var_60
  loc_0041D361: push eax
  loc_0041D362: lea ecx, var_5C
  loc_0041D365: push ecx
  loc_0041D366: push 00000009h
  loc_0041D368: call [00401180h] ; __vbaFreeStrList
  loc_0041D36E: add esp, 00000028h
  loc_0041D371: lea edx, var_84
  loc_0041D377: push edx
  loc_0041D378: lea eax, var_80
  loc_0041D37B: push eax
  loc_0041D37C: push 00000002h
  loc_0041D37E: call [00401040h] ; __vbaFreeObjList
  loc_0041D384: add esp, 0000000Ch
  loc_0041D387: lea ecx, var_C4
  loc_0041D38D: push ecx
  loc_0041D38E: lea edx, var_B4
  loc_0041D394: push edx
  loc_0041D395: lea eax, var_A4
  loc_0041D39B: push eax
  loc_0041D39C: lea ecx, var_94
  loc_0041D3A2: push ecx
  loc_0041D3A3: push 00000004h
  loc_0041D3A5: call [00401038h] ; __vbaFreeVarList
  loc_0041D3AB: add esp, 00000014h
  loc_0041D3AE: mov var_4, 00000029h
  loc_0041D3B5: call 0041ECE0h
  loc_0041D3BA: mov var_4, 0000002Ah
  loc_0041D3C1: call [00401034h] ; __vbaEnd
  loc_0041D3C7: mov var_4, 0000002Dh
  loc_0041D3CE: push 00000000h
  loc_0041D3D0: call [0040107Ch] ; __vbaOnError
  loc_0041D3D6: mov var_4, 0000002Eh
  loc_0041D3DD: movsx edx, var_30
  loc_0041D3E1: test edx, edx
  loc_0041D3E3: jz 0041D65Ah
  loc_0041D3E9: mov var_4, 0000002Fh
  loc_0041D3F0: lea eax, var_44
  loc_0041D3F3: mov var_CC, eax
  loc_0041D3F9: mov var_D4, 0000400Ch
  loc_0041D403: mov eax, 00000010h
  loc_0041D408: call 00401AA0h ; __vbaChkstk
  loc_0041D40D: mov ecx, esp
  loc_0041D40F: mov edx, var_D4
  loc_0041D415: mov [ecx], edx
  loc_0041D417: mov eax, var_D0
  loc_0041D41D: mov [ecx+00000004h], eax
  loc_0041D420: mov edx, var_CC
  loc_0041D426: mov [ecx+00000008h], edx
  loc_0041D429: mov eax, var_C8
  loc_0041D42F: mov [ecx+0000000Ch], eax
  loc_0041D432: push 00000001h
  loc_0041D434: push 00407E6Ch ; "Enter"
  loc_0041D439: mov ecx, var_28
  loc_0041D43C: push ecx
  loc_0041D43D: call [004011A8h] ; __vbaLateMemCall
  loc_0041D443: add esp, 0000001Ch
  loc_0041D446: mov var_4, 00000030h
  loc_0041D44D: lea edx, var_44
  loc_0041D450: push edx
  loc_0041D451: call [00401044h] ; __vbaStrErrVarCopy
  loc_0041D457: mov var_8C, eax
  loc_0041D45D: mov var_94, 00000008h
  loc_0041D467: lea eax, var_94
  loc_0041D46D: push eax
  loc_0041D46E: lea ecx, var_A4
  loc_0041D474: push ecx
  loc_0041D475: call [004010A4h] ; rtcTrimVar
  loc_0041D47B: lea edx, var_A4
  loc_0041D481: push edx
  loc_0041D482: call [00401030h] ; __vbaStrVarMove
  loc_0041D488: mov edx, eax
  loc_0041D48A: lea ecx, var_2C
  loc_0041D48D: call [004011D0h] ; __vbaStrMove
  loc_0041D493: lea eax, var_A4
  loc_0041D499: push eax
  loc_0041D49A: lea ecx, var_94
  loc_0041D4A0: push ecx
  loc_0041D4A1: push 00000002h
  loc_0041D4A3: call [00401038h] ; __vbaFreeVarList
  loc_0041D4A9: add esp, 0000000Ch
  loc_0041D4AC: mov var_4, 00000031h
  loc_0041D4B3: lea edx, var_2C
  loc_0041D4B6: push edx
  loc_0041D4B7: call 0041E210h
  loc_0041D4BC: mov var_4, 00000032h
  loc_0041D4C3: xor eax, eax
  loc_0041D4C5: test eax, eax
  loc_0041D4C7: jz 0041D62Fh
  loc_0041D4CD: movsx ecx, [00423034h]
  loc_0041D4D4: test ecx, ecx
  loc_0041D4D6: jnz 0041D62Fh
  loc_0041D4DC: mov var_4, 00000033h
  loc_0041D4E3: mov var_BC, 80020004h
  loc_0041D4ED: mov var_C4, 0000000Ah
  loc_0041D4F7: mov var_AC, 80020004h
  loc_0041D501: mov var_B4, 0000000Ah
  loc_0041D50B: mov var_CC, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041D515: mov var_D4, 00000008h
  loc_0041D51F: lea edx, var_D4
  loc_0041D525: lea ecx, var_A4
  loc_0041D52B: call [004011B4h] ; __vbaVarDup
  loc_0041D531: push 00407E7Ch ; "In reply to '"
  loc_0041D536: mov edx, arg_10
  loc_0041D539: mov eax, [edx]
  loc_0041D53B: push eax
  loc_0041D53C: call [00401050h] ; __vbaStrCat
  loc_0041D542: mov edx, eax
  loc_0041D544: lea ecx, var_5C
  loc_0041D547: call [004011D0h] ; __vbaStrMove
  loc_0041D54D: push eax
  loc_0041D54E: push 00407E9Ch ; "', "
  loc_0041D553: call [00401050h] ; __vbaStrCat
  loc_0041D559: mov edx, eax
  loc_0041D55B: lea ecx, var_60
  loc_0041D55E: call [004011D0h] ; __vbaStrMove
  loc_0041D564: push eax
  loc_0041D565: mov ecx, arg_C
  loc_0041D568: mov edx, [ecx]
  loc_0041D56A: push edx
  loc_0041D56B: call [00401050h] ; __vbaStrCat
  loc_0041D571: mov edx, eax
  loc_0041D573: lea ecx, var_64
  loc_0041D576: call [004011D0h] ; __vbaStrMove
  loc_0041D57C: push eax
  loc_0041D57D: push 00407EA8h ; " replied:"
  loc_0041D582: call [00401050h] ; __vbaStrCat
  loc_0041D588: mov edx, eax
  loc_0041D58A: lea ecx, var_68
  loc_0041D58D: call [004011D0h] ; __vbaStrMove
  loc_0041D593: push eax
  loc_0041D594: push 004054D8h ; vbCrLf
  loc_0041D599: call [00401050h] ; __vbaStrCat
  loc_0041D59F: mov edx, eax
  loc_0041D5A1: lea ecx, var_6C
  loc_0041D5A4: call [004011D0h] ; __vbaStrMove
  loc_0041D5AA: push eax
  loc_0041D5AB: mov eax, var_2C
  loc_0041D5AE: push eax
  loc_0041D5AF: call [00401050h] ; __vbaStrCat
  loc_0041D5B5: mov var_8C, eax
  loc_0041D5BB: mov var_94, 00000008h
  loc_0041D5C5: lea ecx, var_C4
  loc_0041D5CB: push ecx
  loc_0041D5CC: lea edx, var_B4
  loc_0041D5D2: push edx
  loc_0041D5D3: lea eax, var_A4
  loc_0041D5D9: push eax
  loc_0041D5DA: push 00000000h
  loc_0041D5DC: lea ecx, var_94
  loc_0041D5E2: push ecx
  loc_0041D5E3: call [00401084h] ; rtcMsgBox
  loc_0041D5E9: lea edx, var_6C
  loc_0041D5EC: push edx
  loc_0041D5ED: lea eax, var_68
  loc_0041D5F0: push eax
  loc_0041D5F1: lea ecx, var_64
  loc_0041D5F4: push ecx
  loc_0041D5F5: lea edx, var_60
  loc_0041D5F8: push edx
  loc_0041D5F9: lea eax, var_5C
  loc_0041D5FC: push eax
  loc_0041D5FD: push 00000005h
  loc_0041D5FF: call [00401180h] ; __vbaFreeStrList
  loc_0041D605: add esp, 00000018h
  loc_0041D608: lea ecx, var_C4
  loc_0041D60E: push ecx
  loc_0041D60F: lea edx, var_B4
  loc_0041D615: push edx
  loc_0041D616: lea eax, var_A4
  loc_0041D61C: push eax
  loc_0041D61D: lea ecx, var_94
  loc_0041D623: push ecx
  loc_0041D624: push 00000004h
  loc_0041D626: call [00401038h] ; __vbaFreeVarList
  loc_0041D62C: add esp, 00000014h
  loc_0041D62F: mov var_4, 00000035h
  loc_0041D636: mov edx, var_2C
  loc_0041D639: mov var_CC, edx
  loc_0041D63F: mov var_D4, 00000008h
  loc_0041D649: lea edx, var_D4
  loc_0041D64F: lea ecx, var_54
  loc_0041D652: call [004011C0h] ; __vbaVarCopy
  loc_0041D658: jmp 0041D684h
  loc_0041D65A: mov var_4, 00000037h
  loc_0041D661: mov var_CC, 00000000h
  loc_0041D66B: mov var_D4, 00000008h
  loc_0041D675: lea edx, var_D4
  loc_0041D67B: lea ecx, var_54
  loc_0041D67E: call [004011C0h] ; __vbaVarCopy
  loc_0041D684: mov var_4, 00000039h
  loc_0041D68B: call [004010A0h] ; rtcDoEvents
  loc_0041D691: mov var_4, 0000003Ah
  loc_0041D698: xor eax, eax
  loc_0041D69A: test eax, eax
  loc_0041D69C: jz 0041DABAh
  loc_0041D6A2: movsx ecx, [00423034h]
  loc_0041D6A9: test ecx, ecx
  loc_0041D6AB: jnz 0041DABAh
  loc_0041D6B1: mov var_4, 0000003Bh
  loc_0041D6B8: mov edx, arg_C
  loc_0041D6BB: mov var_CC, edx
  loc_0041D6C1: mov var_D4, 00004008h
  loc_0041D6CB: lea eax, var_D4
  loc_0041D6D1: push eax
  loc_0041D6D2: lea ecx, var_94
  loc_0041D6D8: push ecx
  loc_0041D6D9: call [004010D4h] ; rtcUpperCaseVar
  loc_0041D6DF: lea edx, var_94
  loc_0041D6E5: lea ecx, var_16C
  loc_0041D6EB: call [00401014h] ; __vbaVarMove
  loc_0041D6F1: mov var_4, 0000003Ch
  loc_0041D6F8: mov var_CC, 00407EC0h ; "RELAY1"
  loc_0041D702: mov var_D4, 00008008h
  loc_0041D70C: lea edx, var_16C
  loc_0041D712: push edx
  loc_0041D713: lea eax, var_D4
  loc_0041D719: push eax
  loc_0041D71A: call [004010E4h] ; __vbaVarTstEq
  loc_0041D720: movsx ecx, ax
  loc_0041D723: test ecx, ecx
  loc_0041D725: jnz 0041D888h
  loc_0041D72B: mov var_DC, 00407ED4h ; "RELAY3"
  loc_0041D735: mov var_E4, 00008008h
  loc_0041D73F: lea edx, var_16C
  loc_0041D745: push edx
  loc_0041D746: lea eax, var_E4
  loc_0041D74C: push eax
  loc_0041D74D: call [004010E4h] ; __vbaVarTstEq
  loc_0041D753: movsx ecx, ax
  loc_0041D756: test ecx, ecx
  loc_0041D758: jnz 0041D888h
  loc_0041D75E: mov var_EC, 00407EE8h ; "RELAY4"
  loc_0041D768: mov var_F4, 00008008h
  loc_0041D772: lea edx, var_16C
  loc_0041D778: push edx
  loc_0041D779: lea eax, var_F4
  loc_0041D77F: push eax
  loc_0041D780: call [004010E4h] ; __vbaVarTstEq
  loc_0041D786: movsx ecx, ax
  loc_0041D789: test ecx, ecx
  loc_0041D78B: jnz 0041D888h
  loc_0041D791: mov var_FC, 00407EFCh ; "RELAY5"
  loc_0041D79B: mov var_104, 00008008h
  loc_0041D7A5: lea edx, var_16C
  loc_0041D7AB: push edx
  loc_0041D7AC: lea eax, var_104
  loc_0041D7B2: push eax
  loc_0041D7B3: call [004010E4h] ; __vbaVarTstEq
  loc_0041D7B9: movsx ecx, ax
  loc_0041D7BC: test ecx, ecx
  loc_0041D7BE: jnz 0041D888h
  loc_0041D7C4: mov var_10C, 00407F10h ; "FET1"
  loc_0041D7CE: mov var_114, 00008008h
  loc_0041D7D8: lea edx, var_16C
  loc_0041D7DE: push edx
  loc_0041D7DF: lea eax, var_114
  loc_0041D7E5: push eax
  loc_0041D7E6: call [004010E4h] ; __vbaVarTstEq
  loc_0041D7EC: movsx ecx, ax
  loc_0041D7EF: test ecx, ecx
  loc_0041D7F1: jnz 0041D888h
  loc_0041D7F7: mov var_11C, 00407F20h ; "FET2"
  loc_0041D801: mov var_124, 00008008h
  loc_0041D80B: lea edx, var_16C
  loc_0041D811: push edx
  loc_0041D812: lea eax, var_124
  loc_0041D818: push eax
  loc_0041D819: call [004010E4h] ; __vbaVarTstEq
  loc_0041D81F: movsx ecx, ax
  loc_0041D822: test ecx, ecx
  loc_0041D824: jnz 0041D888h
  loc_0041D826: mov var_12C, 00407F30h ; "FET3"
  loc_0041D830: mov var_134, 00008008h
  loc_0041D83A: lea edx, var_16C
  loc_0041D840: push edx
  loc_0041D841: lea eax, var_134
  loc_0041D847: push eax
  loc_0041D848: call [004010E4h] ; __vbaVarTstEq
  loc_0041D84E: movsx ecx, ax
  loc_0041D851: test ecx, ecx
  loc_0041D853: jnz 0041D888h
  loc_0041D855: mov var_13C, 00407F40h ; "FET4"
  loc_0041D85F: mov var_144, 00008008h
  loc_0041D869: lea edx, var_16C
  loc_0041D86F: push edx
  loc_0041D870: lea eax, var_144
  loc_0041D876: push eax
  loc_0041D877: call [004010E4h] ; __vbaVarTstEq
  loc_0041D87D: movsx ecx, ax
  loc_0041D880: test ecx, ecx
  loc_0041D882: jz 0041DABAh
  loc_0041D888: mov var_4, 0000003Dh
  loc_0041D88F: mov var_CC, 00407F50h ; "SYST:ERR?"
  loc_0041D899: mov var_D4, 00000008h
  loc_0041D8A3: mov eax, 00000010h
  loc_0041D8A8: call 00401AA0h ; __vbaChkstk
  loc_0041D8AD: mov edx, esp
  loc_0041D8AF: mov eax, var_D4
  loc_0041D8B5: mov [edx], eax
  loc_0041D8B7: mov ecx, var_D0
  loc_0041D8BD: mov [edx+00000004h], ecx
  loc_0041D8C0: mov eax, var_CC
  loc_0041D8C6: mov [edx+00000008h], eax
  loc_0041D8C9: mov ecx, var_C8
  loc_0041D8CF: mov [edx+0000000Ch], ecx
  loc_0041D8D2: push 00000001h
  loc_0041D8D4: push 00407DB4h ; "Output"
  loc_0041D8D9: mov edx, var_28
  loc_0041D8DC: push edx
  loc_0041D8DD: call [004011A8h] ; __vbaLateMemCall
  loc_0041D8E3: add esp, 0000001Ch
  loc_0041D8E6: mov var_4, 0000003Eh
  loc_0041D8ED: lea eax, var_44
  loc_0041D8F0: mov var_CC, eax
  loc_0041D8F6: mov var_D4, 0000400Ch
  loc_0041D900: mov eax, 00000010h
  loc_0041D905: call 00401AA0h ; __vbaChkstk
  loc_0041D90A: mov ecx, esp
  loc_0041D90C: mov edx, var_D4
  loc_0041D912: mov [ecx], edx
  loc_0041D914: mov eax, var_D0
  loc_0041D91A: mov [ecx+00000004h], eax
  loc_0041D91D: mov edx, var_CC
  loc_0041D923: mov [ecx+00000008h], edx
  loc_0041D926: mov eax, var_C8
  loc_0041D92C: mov [ecx+0000000Ch], eax
  loc_0041D92F: push 00000001h
  loc_0041D931: push 00407E6Ch ; "Enter"
  loc_0041D936: mov ecx, var_28
  loc_0041D939: push ecx
  loc_0041D93A: call [004011A8h] ; __vbaLateMemCall
  loc_0041D940: add esp, 0000001Ch
  loc_0041D943: mov var_4, 0000003Fh
  loc_0041D94A: lea edx, var_44
  loc_0041D94D: push edx
  loc_0041D94E: call [00401044h] ; __vbaStrErrVarCopy
  loc_0041D954: mov var_8C, eax
  loc_0041D95A: mov var_94, 00000008h
  loc_0041D964: lea eax, var_94
  loc_0041D96A: push eax
  loc_0041D96B: lea ecx, var_A4
  loc_0041D971: push ecx
  loc_0041D972: call [004010A4h] ; rtcTrimVar
  loc_0041D978: lea edx, var_A4
  loc_0041D97E: push edx
  loc_0041D97F: call [00401030h] ; __vbaStrVarMove
  loc_0041D985: mov edx, eax
  loc_0041D987: lea ecx, var_2C
  loc_0041D98A: call [004011D0h] ; __vbaStrMove
  loc_0041D990: lea eax, var_A4
  loc_0041D996: push eax
  loc_0041D997: lea ecx, var_94
  loc_0041D99D: push ecx
  loc_0041D99E: push 00000002h
  loc_0041D9A0: call [00401038h] ; __vbaFreeVarList
  loc_0041D9A6: add esp, 0000000Ch
  loc_0041D9A9: mov var_4, 00000040h
  loc_0041D9B0: lea edx, var_2C
  loc_0041D9B3: push edx
  loc_0041D9B4: call 0041E210h
  loc_0041D9B9: mov var_4, 00000041h
  loc_0041D9C0: mov var_BC, 80020004h
  loc_0041D9CA: mov var_C4, 0000000Ah
  loc_0041D9D4: mov var_AC, 80020004h
  loc_0041D9DE: mov var_B4, 0000000Ah
  loc_0041D9E8: mov var_CC, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041D9F2: mov var_D4, 00000008h
  loc_0041D9FC: lea edx, var_D4
  loc_0041DA02: lea ecx, var_A4
  loc_0041DA08: call [004011B4h] ; __vbaVarDup
  loc_0041DA0E: mov eax, arg_C
  loc_0041DA11: mov ecx, [eax]
  loc_0041DA13: push ecx
  loc_0041DA14: push 00407F90h ; ", when asked SYST:Err? replied "
  loc_0041DA19: call [00401050h] ; __vbaStrCat
  loc_0041DA1F: mov edx, eax
  loc_0041DA21: lea ecx, var_5C
  loc_0041DA24: call [004011D0h] ; __vbaStrMove
  loc_0041DA2A: push eax
  loc_0041DA2B: push 004054D8h ; vbCrLf
  loc_0041DA30: call [00401050h] ; __vbaStrCat
  loc_0041DA36: mov edx, eax
  loc_0041DA38: lea ecx, var_60
  loc_0041DA3B: call [004011D0h] ; __vbaStrMove
  loc_0041DA41: push eax
  loc_0041DA42: mov edx, var_2C
  loc_0041DA45: push edx
  loc_0041DA46: call [00401050h] ; __vbaStrCat
  loc_0041DA4C: mov var_8C, eax
  loc_0041DA52: mov var_94, 00000008h
  loc_0041DA5C: lea eax, var_C4
  loc_0041DA62: push eax
  loc_0041DA63: lea ecx, var_B4
  loc_0041DA69: push ecx
  loc_0041DA6A: lea edx, var_A4
  loc_0041DA70: push edx
  loc_0041DA71: push 00000000h
  loc_0041DA73: lea eax, var_94
  loc_0041DA79: push eax
  loc_0041DA7A: call [00401084h] ; rtcMsgBox
  loc_0041DA80: lea ecx, var_60
  loc_0041DA83: push ecx
  loc_0041DA84: lea edx, var_5C
  loc_0041DA87: push edx
  loc_0041DA88: push 00000002h
  loc_0041DA8A: call [00401180h] ; __vbaFreeStrList
  loc_0041DA90: add esp, 0000000Ch
  loc_0041DA93: lea eax, var_C4
  loc_0041DA99: push eax
  loc_0041DA9A: lea ecx, var_B4
  loc_0041DAA0: push ecx
  loc_0041DAA1: lea edx, var_A4
  loc_0041DAA7: push edx
  loc_0041DAA8: lea eax, var_94
  loc_0041DAAE: push eax
  loc_0041DAAF: push 00000004h
  loc_0041DAB1: call [00401038h] ; __vbaFreeVarList
  loc_0041DAB7: add esp, 00000014h
  loc_0041DABA: push 0041DB75h
  loc_0041DABF: jmp 0041DB44h
  loc_0041DAC4: mov ecx, var_10
  loc_0041DAC7: and ecx, 00000004h
  loc_0041DACA: test ecx, ecx
  loc_0041DACC: jz 0041DAD7h
  loc_0041DACE: lea ecx, var_54
  loc_0041DAD1: call [00401020h] ; __vbaFreeVar
  loc_0041DAD7: lea edx, var_7C
  loc_0041DADA: push edx
  loc_0041DADB: lea eax, var_78
  loc_0041DADE: push eax
  loc_0041DADF: lea ecx, var_74
  loc_0041DAE2: push ecx
  loc_0041DAE3: lea edx, var_70
  loc_0041DAE6: push edx
  loc_0041DAE7: lea eax, var_6C
  loc_0041DAEA: push eax
  loc_0041DAEB: lea ecx, var_68
  loc_0041DAEE: push ecx
  loc_0041DAEF: lea edx, var_64
  loc_0041DAF2: push edx
  loc_0041DAF3: lea eax, var_60
  loc_0041DAF6: push eax
  loc_0041DAF7: lea ecx, var_5C
  loc_0041DAFA: push ecx
  loc_0041DAFB: push 00000009h
  loc_0041DAFD: call [00401180h] ; __vbaFreeStrList
  loc_0041DB03: add esp, 00000028h
  loc_0041DB06: lea edx, var_84
  loc_0041DB0C: push edx
  loc_0041DB0D: lea eax, var_80
  loc_0041DB10: push eax
  loc_0041DB11: push 00000002h
  loc_0041DB13: call [00401040h] ; __vbaFreeObjList
  loc_0041DB19: add esp, 0000000Ch
  loc_0041DB1C: lea ecx, var_C4
  loc_0041DB22: push ecx
  loc_0041DB23: lea edx, var_B4
  loc_0041DB29: push edx
  loc_0041DB2A: lea eax, var_A4
  loc_0041DB30: push eax
  loc_0041DB31: lea ecx, var_94
  loc_0041DB37: push ecx
  loc_0041DB38: push 00000004h
  loc_0041DB3A: call [00401038h] ; __vbaFreeVarList
  loc_0041DB40: add esp, 00000014h
  loc_0041DB43: ret
  loc_0041DB44: lea ecx, var_16C
  loc_0041DB4A: call [00401020h] ; __vbaFreeVar
  loc_0041DB50: lea ecx, var_28
  loc_0041DB53: call [004011F0h] ; __vbaFreeObj
  loc_0041DB59: lea ecx, var_2C
  loc_0041DB5C: call [004011F4h] ; __vbaFreeStr
  loc_0041DB62: lea ecx, var_44
  loc_0041DB65: call [00401020h] ; __vbaFreeVar
  loc_0041DB6B: lea ecx, var_58
  loc_0041DB6E: call [004011F4h] ; __vbaFreeStr
  loc_0041DB74: ret
  loc_0041DB75: mov edx, arg_8
  loc_0041DB78: mov eax, var_54
  loc_0041DB7B: mov [edx], eax
  loc_0041DB7D: mov ecx, var_50
  loc_0041DB80: mov [edx+00000004h], ecx
  loc_0041DB83: mov eax, var_4C
  loc_0041DB86: mov [edx+00000008h], eax
  loc_0041DB89: mov ecx, var_48
  loc_0041DB8C: mov [edx+0000000Ch], ecx
  loc_0041DB8F: mov eax, arg_8
  loc_0041DB92: mov ecx, var_20
  loc_0041DB95: mov fs:[00000000h], ecx
  loc_0041DB9C: pop edi
  loc_0041DB9D: pop esi
  loc_0041DB9E: pop ebx
  loc_0041DB9F: mov esp, ebp
  loc_0041DBA1: pop ebp
  loc_0041DBA2: retn 0010h
End Function

Private Sub Proc_2_1_41DC40(arg_C) '41DC40
  loc_0041DC40: push ebp
  loc_0041DC41: mov ebp, esp
  loc_0041DC43: sub esp, 00000008h
  loc_0041DC46: push 00401AA6h ; __vbaExceptHandler
  loc_0041DC4B: mov eax, fs:[00000000h]
  loc_0041DC51: push eax
  loc_0041DC52: mov fs:[00000000h], esp
  loc_0041DC59: sub esp, 0000003Ch
  loc_0041DC5C: push ebx
  loc_0041DC5D: push esi
  loc_0041DC5E: push edi
  loc_0041DC5F: mov var_8, esp
  loc_0041DC62: mov var_4, 00401808h
  loc_0041DC69: mov edx, arg_8
  loc_0041DC6C: mov esi, [0040101Ch] ; __vbaVarVargNofree
  loc_0041DC72: xor eax, eax
  loc_0041DC74: lea ecx, var_38
  loc_0041DC77: mov var_28, eax
  loc_0041DC7A: mov var_38, eax
  loc_0041DC7D: mov var_48, eax
  loc_0041DC80: call __vbaVarVargNofree
  loc_0041DC82: mov edx, arg_C
  loc_0041DC85: push eax
  loc_0041DC86: lea ecx, var_48
  loc_0041DC89: call __vbaVarVargNofree
  loc_0041DC8B: push eax
  loc_0041DC8C: lea eax, var_28
  loc_0041DC8F: push eax
  loc_0041DC90: call [00401000h] ; __vbaVarSub
  loc_0041DC96: push eax
  loc_0041DC97: call [00401134h] ; __vbaR8ErrVar
  loc_0041DC9D: cmp [00423000h], 00000000h
  loc_0041DCA4: jnz 0041DCAEh
  loc_0041DCA6: fdiv st0, real8 ptr [00401800h]
  loc_0041DCAC: jmp 0041DCBFh
  loc_0041DCAE: push [00401804h]
  loc_0041DCB4: push [00401800h]
  loc_0041DCBA: call 00401AC4h ; _adj_fdiv_m64
  loc_0041DCBF: push 0041DCDBh
  loc_0041DCC4: fstp real8 ptr var_18
  loc_0041DCC7: fnstsw ax
  loc_0041DCC9: test al, 0Dh
  loc_0041DCCB: jnz 0041DCF1h
  loc_0041DCCD: fwait
  loc_0041DCCE: jmp 0041DCDAh
  loc_0041DCD0: lea ecx, var_28
  loc_0041DCD3: call [00401020h] ; __vbaFreeVar
  loc_0041DCD9: ret
  loc_0041DCDA: ret
  loc_0041DCDB: mov ecx, var_10
  loc_0041DCDE: pop edi
  loc_0041DCDF: fld real8 ptr var_18
  loc_0041DCE2: pop esi
  loc_0041DCE3: mov fs:[00000000h], ecx
  loc_0041DCEA: pop ebx
  loc_0041DCEB: mov esp, ebp
  loc_0041DCED: pop ebp
  loc_0041DCEE: retn 0008h
End Sub

Private Sub Proc_2_2_41DD00() '41DD00
  loc_0041DD00: push ebp
  loc_0041DD01: mov ebp, esp
  loc_0041DD03: sub esp, 00000008h
  loc_0041DD06: push 00401AA6h ; __vbaExceptHandler
  loc_0041DD0B: mov eax, fs:[00000000h]
  loc_0041DD11: push eax
  loc_0041DD12: mov fs:[00000000h], esp
  loc_0041DD19: sub esp, 000000B8h
  loc_0041DD1F: push ebx
  loc_0041DD20: push esi
  loc_0041DD21: push edi
  loc_0041DD22: mov var_8, esp
  loc_0041DD25: mov var_4, 00401818h
  loc_0041DD2C: xor esi, esi
  loc_0041DD2E: mov edx, 00407FD4h ; "SELECT * FROM tblTestSerial"
  loc_0041DD33: lea ecx, var_14
  loc_0041DD36: mov var_14, esi
  loc_0041DD39: mov var_18, esi
  loc_0041DD3C: mov var_24, esi
  loc_0041DD3F: mov var_28, esi
  loc_0041DD42: mov var_38, esi
  loc_0041DD45: mov var_48, esi
  loc_0041DD48: mov var_58, esi
  loc_0041DD4B: mov var_68, esi
  loc_0041DD4E: mov var_78, esi
  loc_0041DD51: mov var_88, esi
  loc_0041DD57: mov var_AC, esi
  loc_0041DD5D: mov var_B0, esi
  loc_0041DD63: call [00401178h] ; __vbaStrCopy
  loc_0041DD69: push 0040714Ch
  loc_0041DD6E: call [00401110h] ; __vbaNew
  loc_0041DD74: push eax
  loc_0041DD75: lea eax, var_18
  loc_0041DD78: push eax
  loc_0041DD79: call [00401080h] ; __vbaObjSet
  loc_0041DD7F: mov eax, var_18
  loc_0041DD82: push 00000002h
  loc_0041DD84: push eax
  loc_0041DD85: mov ecx, [eax]
  loc_0041DD87: call [ecx+0000005Ch]
  loc_0041DD8A: cmp eax, esi
  loc_0041DD8C: fnclex
  loc_0041DD8E: jge 0041DDA2h
  loc_0041DD90: mov edx, var_18
  loc_0041DD93: push 0000005Ch
  loc_0041DD95: push 004072E8h
  loc_0041DD9A: push edx
  loc_0041DD9B: push eax
  loc_0041DD9C: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041DDA2: mov eax, var_18
  loc_0041DDA5: push 00000002h
  loc_0041DDA7: push eax
  loc_0041DDA8: mov ecx, [eax]
  loc_0041DDAA: call [ecx+0000004Ch]
  loc_0041DDAD: cmp eax, esi
  loc_0041DDAF: fnclex
  loc_0041DDB1: jge 0041DDC5h
  loc_0041DDB3: mov edx, var_18
  loc_0041DDB6: push 0000004Ch
  loc_0041DDB8: push 004072E8h
  loc_0041DDBD: push edx
  loc_0041DDBE: push eax
  loc_0041DDBF: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041DDC5: push FFFFFFFFh
  loc_0041DDC7: push FFFFFFFFh
  loc_0041DDC9: mov eax, arg_8
  loc_0041DDCC: push FFFFFFFFh
  loc_0041DDCE: sub esp, 00000010h
  loc_0041DDD1: mov ecx, 00000009h
  loc_0041DDD6: mov eax, [eax]
  loc_0041DDD8: mov ebx, esp
  loc_0041DDDA: mov var_88, ecx
  loc_0041DDE0: sub esp, 00000010h
  loc_0041DDE3: mov [ebx], ecx
  loc_0041DDE5: mov ecx, var_84
  loc_0041DDEB: mov var_80, eax
  loc_0041DDEE: mov edx, var_14
  loc_0041DDF1: mov [ebx+00000004h], ecx
  loc_0041DDF4: mov edi, var_18
  loc_0041DDF7: mov ecx, esp
  loc_0041DDF9: mov esi, 00000008h
  loc_0041DDFE: mov [ebx+00000008h], eax
  loc_0041DE01: mov eax, var_7C
  loc_0041DE04: mov var_70, edx
  loc_0041DE07: mov var_78, esi
  loc_0041DE0A: mov edi, [edi]
  loc_0041DE0C: mov [ebx+0000000Ch], eax
  loc_0041DE0F: mov eax, var_74
  loc_0041DE12: mov [ecx], esi
  loc_0041DE14: mov [ecx+00000004h], eax
  loc_0041DE17: mov eax, var_18
  loc_0041DE1A: push eax
  loc_0041DE1B: mov [ecx+00000008h], edx
  loc_0041DE1E: mov edx, var_6C
  loc_0041DE21: mov [ecx+0000000Ch], edx
  loc_0041DE24: call [edi+000000A0h]
  loc_0041DE2A: test eax, eax
  loc_0041DE2C: fnclex
  loc_0041DE2E: jge 0041DE49h
  loc_0041DE30: mov ecx, var_18
  loc_0041DE33: mov edi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041DE39: push 000000A0h
  loc_0041DE3E: push 004072E8h
  loc_0041DE43: push ecx
  loc_0041DE44: push eax
  loc_0041DE45: call edi
  loc_0041DE47: jmp 0041DE4Fh
  loc_0041DE49: mov edi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041DE4F: mov eax, var_18
  loc_0041DE52: lea ecx, var_AC
  loc_0041DE58: push ecx
  loc_0041DE59: push eax
  loc_0041DE5A: mov edx, [eax]
  loc_0041DE5C: call [edx+00000050h]
  loc_0041DE5F: test eax, eax
  loc_0041DE61: fnclex
  loc_0041DE63: jge 0041DE73h
  loc_0041DE65: mov edx, var_18
  loc_0041DE68: push 00000050h
  loc_0041DE6A: push 004072E8h
  loc_0041DE6F: push edx
  loc_0041DE70: push eax
  loc_0041DE71: call edi
  loc_0041DE73: mov eax, var_18
  loc_0041DE76: lea edx, var_B0
  loc_0041DE7C: push edx
  loc_0041DE7D: push eax
  loc_0041DE7E: mov ecx, [eax]
  loc_0041DE80: call [ecx+00000034h]
  loc_0041DE83: test eax, eax
  loc_0041DE85: fnclex
  loc_0041DE87: jge 0041DE97h
  loc_0041DE89: mov ecx, var_18
  loc_0041DE8C: push 00000034h
  loc_0041DE8E: push 004072E8h
  loc_0041DE93: push ecx
  loc_0041DE94: push eax
  loc_0041DE95: call edi
  loc_0041DE97: xor edx, edx
  loc_0041DE99: cmp var_B0, dx
  loc_0041DEA0: setz dl
  loc_0041DEA3: xor eax, eax
  loc_0041DEA5: cmp var_AC, ax
  loc_0041DEAC: setz al
  loc_0041DEAF: or edx, eax
  loc_0041DEB1: jnz 0041DF3Bh
  loc_0041DEB7: mov esi, [004011B4h] ; __vbaVarDup
  loc_0041DEBD: mov ecx, 0000000Ah
  loc_0041DEC2: mov eax, 80020004h
  loc_0041DEC7: mov var_68, ecx
  loc_0041DECA: mov var_58, ecx
  loc_0041DECD: mov ebx, 00000008h
  loc_0041DED2: lea edx, var_88
  loc_0041DED8: lea ecx, var_48
  loc_0041DEDB: mov var_60, eax
  loc_0041DEDE: mov var_50, eax
  loc_0041DEE1: mov var_80, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041DEE8: mov var_88, ebx
  loc_0041DEEE: call __vbaVarDup
  loc_0041DEF0: lea edx, var_78
  loc_0041DEF3: lea ecx, var_38
  loc_0041DEF6: mov var_70, 00408010h ; "Major Error! Cannot retrieve Test Serial. Program ending!"
  loc_0041DEFD: mov var_78, ebx
  loc_0041DF00: call __vbaVarDup
  loc_0041DF02: lea ecx, var_68
  loc_0041DF05: lea edx, var_58
  loc_0041DF08: push ecx
  loc_0041DF09: lea eax, var_48
  loc_0041DF0C: push edx
  loc_0041DF0D: push eax
  loc_0041DF0E: lea ecx, var_38
  loc_0041DF11: push 00000010h
  loc_0041DF13: push ecx
  loc_0041DF14: call [00401084h] ; rtcMsgBox
  loc_0041DF1A: lea edx, var_68
  loc_0041DF1D: lea eax, var_58
  loc_0041DF20: push edx
  loc_0041DF21: lea ecx, var_48
  loc_0041DF24: push eax
  loc_0041DF25: lea edx, var_38
  loc_0041DF28: push ecx
  loc_0041DF29: push edx
  loc_0041DF2A: push 00000004h
  loc_0041DF2C: call [00401038h] ; __vbaFreeVarList
  loc_0041DF32: add esp, 00000014h
  loc_0041DF35: call [00401034h] ; __vbaEnd
  loc_0041DF3B: mov eax, var_18
  loc_0041DF3E: push eax
  loc_0041DF3F: mov ecx, [eax]
  loc_0041DF41: call [ecx+00000098h]
  loc_0041DF47: test eax, eax
  loc_0041DF49: fnclex
  loc_0041DF4B: jge 0041DF5Eh
  loc_0041DF4D: mov edx, var_18
  loc_0041DF50: push 00000098h
  loc_0041DF55: push 004072E8h
  loc_0041DF5A: push edx
  loc_0041DF5B: push eax
  loc_0041DF5C: call edi
  loc_0041DF5E: mov eax, var_18
  loc_0041DF61: lea edx, var_24
  loc_0041DF64: push edx
  loc_0041DF65: push eax
  loc_0041DF66: mov ecx, [eax]
  loc_0041DF68: call [ecx+00000054h]
  loc_0041DF6B: test eax, eax
  loc_0041DF6D: fnclex
  loc_0041DF6F: jge 0041DF7Fh
  loc_0041DF71: mov ecx, var_18
  loc_0041DF74: push 00000054h
  loc_0041DF76: push 004072E8h
  loc_0041DF7B: push ecx
  loc_0041DF7C: push eax
  loc_0041DF7D: call edi
  loc_0041DF7F: lea ebx, var_28
  loc_0041DF82: mov eax, var_24
  loc_0041DF85: push ebx
  loc_0041DF86: mov edx, 00000008h
  loc_0041DF8B: sub esp, 00000010h
  loc_0041DF8E: mov var_78, edx
  loc_0041DF91: mov ebx, esp
  loc_0041DF93: mov ecx, 00407804h ; "fldTestSerial"
  loc_0041DF98: mov var_70, ecx
  loc_0041DF9B: mov edi, [eax]
  loc_0041DF9D: mov [ebx], edx
  loc_0041DF9F: mov edx, var_74
  loc_0041DFA2: push eax
  loc_0041DFA3: mov esi, eax
  loc_0041DFA5: mov [ebx+00000004h], edx
  loc_0041DFA8: mov [ebx+00000008h], ecx
  loc_0041DFAB: mov ecx, var_6C
  loc_0041DFAE: mov [ebx+0000000Ch], ecx
  loc_0041DFB1: call [edi+00000028h]
  loc_0041DFB4: test eax, eax
  loc_0041DFB6: fnclex
  loc_0041DFB8: jge 0041DFCDh
  loc_0041DFBA: mov edi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041DFC0: push 00000028h
  loc_0041DFC2: push 00407390h
  loc_0041DFC7: push esi
  loc_0041DFC8: push eax
  loc_0041DFC9: call edi
  loc_0041DFCB: jmp 0041DFD3h
  loc_0041DFCD: mov edi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041DFD3: mov eax, var_28
  loc_0041DFD6: lea ecx, var_38
  loc_0041DFD9: push ecx
  loc_0041DFDA: push eax
  loc_0041DFDB: mov edx, [eax]
  loc_0041DFDD: mov esi, eax
  loc_0041DFDF: call [edx+00000034h]
  loc_0041DFE2: test eax, eax
  loc_0041DFE4: fnclex
  loc_0041DFE6: jge 0041DFF3h
  loc_0041DFE8: push 00000034h
  loc_0041DFEA: push 004073A0h
  loc_0041DFEF: push esi
  loc_0041DFF0: push eax
  loc_0041DFF1: call edi
  loc_0041DFF3: lea edx, var_38
  loc_0041DFF6: push edx
  loc_0041DFF7: call [0040119Ch] ; __vbaI4Var
  loc_0041DFFD: mov var_1C, eax
  loc_0041E000: lea eax, var_28
  loc_0041E003: lea ecx, var_24
  loc_0041E006: push eax
  loc_0041E007: push ecx
  loc_0041E008: push 00000002h
  loc_0041E00A: call [00401040h] ; __vbaFreeObjList
  loc_0041E010: add esp, 0000000Ch
  loc_0041E013: lea ecx, var_38
  loc_0041E016: call [00401020h] ; __vbaFreeVar
  loc_0041E01C: mov eax, var_18
  loc_0041E01F: lea ecx, var_24
  loc_0041E022: push ecx
  loc_0041E023: push eax
  loc_0041E024: mov edx, [eax]
  loc_0041E026: call [edx+00000054h]
  loc_0041E029: test eax, eax
  loc_0041E02B: fnclex
  loc_0041E02D: jge 0041E03Dh
  loc_0041E02F: mov edx, var_18
  loc_0041E032: push 00000054h
  loc_0041E034: push 004072E8h
  loc_0041E039: push edx
  loc_0041E03A: push eax
  loc_0041E03B: call edi
  loc_0041E03D: lea ebx, var_28
  loc_0041E040: mov eax, var_24
  loc_0041E043: push ebx
  loc_0041E044: mov edx, 00000008h
  loc_0041E049: sub esp, 00000010h
  loc_0041E04C: mov var_78, edx
  loc_0041E04F: mov ebx, esp
  loc_0041E051: mov ecx, 00407804h ; "fldTestSerial"
  loc_0041E056: mov var_70, ecx
  loc_0041E059: mov edi, [eax]
  loc_0041E05B: mov [ebx], edx
  loc_0041E05D: mov edx, var_74
  loc_0041E060: push eax
  loc_0041E061: mov esi, eax
  loc_0041E063: mov [ebx+00000004h], edx
  loc_0041E066: mov [ebx+00000008h], ecx
  loc_0041E069: mov ecx, var_6C
  loc_0041E06C: mov [ebx+0000000Ch], ecx
  loc_0041E06F: call [edi+00000028h]
  loc_0041E072: test eax, eax
  loc_0041E074: fnclex
  loc_0041E076: jge 0041E087h
  loc_0041E078: push 00000028h
  loc_0041E07A: push 00407390h
  loc_0041E07F: push esi
  loc_0041E080: push eax
  loc_0041E081: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041E087: mov eax, var_1C
  loc_0041E08A: mov ecx, var_28
  loc_0041E08D: add eax, 00000001h
  loc_0041E090: mov edx, 00000003h
  loc_0041E095: jo 0041E1FFh
  loc_0041E09B: sub esp, 00000010h
  loc_0041E09E: mov var_88, edx
  loc_0041E0A4: mov ebx, esp
  loc_0041E0A6: mov var_80, eax
  loc_0041E0A9: mov edi, [ecx]
  loc_0041E0AB: push ecx
  loc_0041E0AC: mov [ebx], edx
  loc_0041E0AE: mov edx, var_84
  loc_0041E0B4: mov esi, ecx
  loc_0041E0B6: mov [ebx+00000004h], edx
  loc_0041E0B9: mov [ebx+00000008h], eax
  loc_0041E0BC: mov eax, var_7C
  loc_0041E0BF: mov [ebx+0000000Ch], eax
  loc_0041E0C2: call [edi+00000038h]
  loc_0041E0C5: test eax, eax
  loc_0041E0C7: fnclex
  loc_0041E0C9: jge 0041E0DAh
  loc_0041E0CB: push 00000038h
  loc_0041E0CD: push 004073A0h
  loc_0041E0D2: push esi
  loc_0041E0D3: push eax
  loc_0041E0D4: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041E0DA: lea ecx, var_28
  loc_0041E0DD: lea edx, var_24
  loc_0041E0E0: push ecx
  loc_0041E0E1: push edx
  loc_0041E0E2: push 00000002h
  loc_0041E0E4: call [00401040h] ; __vbaFreeObjList
  loc_0041E0EA: mov ecx, 0000000Ah
  loc_0041E0EF: mov eax, 80020004h
  loc_0041E0F4: push ecx
  loc_0041E0F5: mov var_88, ecx
  loc_0041E0FB: mov ebx, esp
  loc_0041E0FD: mov esi, ecx
  loc_0041E0FF: sub esp, 00000010h
  loc_0041E102: mov var_80, eax
  loc_0041E105: mov [ebx], ecx
  loc_0041E107: mov ecx, var_84
  loc_0041E10D: mov edx, eax
  loc_0041E10F: mov edi, var_18
  loc_0041E112: mov [ebx+00000004h], ecx
  loc_0041E115: mov ecx, esp
  loc_0041E117: mov var_70, edx
  loc_0041E11A: mov var_78, esi
  loc_0041E11D: mov [ebx+00000008h], eax
  loc_0041E120: mov eax, var_7C
  loc_0041E123: mov edi, [edi]
  loc_0041E125: mov [ebx+0000000Ch], eax
  loc_0041E128: mov eax, var_74
  loc_0041E12B: mov [ecx], esi
  loc_0041E12D: mov [ecx+00000004h], eax
  loc_0041E130: mov eax, var_18
  loc_0041E133: push eax
  loc_0041E134: mov [ecx+00000008h], edx
  loc_0041E137: mov edx, var_6C
  loc_0041E13A: mov [ecx+0000000Ch], edx
  loc_0041E13D: call [edi+000000ACh]
  loc_0041E143: test eax, eax
  loc_0041E145: fnclex
  loc_0041E147: jge 0041E15Eh
  loc_0041E149: mov ecx, var_18
  loc_0041E14C: push 000000ACh
  loc_0041E151: push 004072E8h
  loc_0041E156: push ecx
  loc_0041E157: push eax
  loc_0041E158: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041E15E: mov eax, var_18
  loc_0041E161: push eax
  loc_0041E162: mov edx, [eax]
  loc_0041E164: call [edx+00000080h]
  loc_0041E16A: test eax, eax
  loc_0041E16C: fnclex
  loc_0041E16E: jge 0041E185h
  loc_0041E170: mov ecx, var_18
  loc_0041E173: push 00000080h
  loc_0041E178: push 004072E8h
  loc_0041E17D: push ecx
  loc_0041E17E: push eax
  loc_0041E17F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041E185: push 0040713Ch
  loc_0041E18A: push 00000000h
  loc_0041E18C: call [004011D4h] ; __vbaCastObj
  loc_0041E192: lea edx, var_18
  loc_0041E195: push eax
  loc_0041E196: push edx
  loc_0041E197: call [00401080h] ; __vbaObjSet
  loc_0041E19D: mov eax, var_1C
  loc_0041E1A0: push 0041E1E9h
  loc_0041E1A5: mov var_20, eax
  loc_0041E1A8: jmp 0041E1D6h
  loc_0041E1AA: lea ecx, var_28
  loc_0041E1AD: lea edx, var_24
  loc_0041E1B0: push ecx
  loc_0041E1B1: push edx
  loc_0041E1B2: push 00000002h
  loc_0041E1B4: call [00401040h] ; __vbaFreeObjList
  loc_0041E1BA: lea eax, var_68
  loc_0041E1BD: lea ecx, var_58
  loc_0041E1C0: push eax
  loc_0041E1C1: lea edx, var_48
  loc_0041E1C4: push ecx
  loc_0041E1C5: lea eax, var_38
  loc_0041E1C8: push edx
  loc_0041E1C9: push eax
  loc_0041E1CA: push 00000004h
  loc_0041E1CC: call [00401038h] ; __vbaFreeVarList
  loc_0041E1D2: add esp, 00000020h
  loc_0041E1D5: ret
  loc_0041E1D6: lea ecx, var_14
  loc_0041E1D9: call [004011F4h] ; __vbaFreeStr
  loc_0041E1DF: lea ecx, var_18
  loc_0041E1E2: call [004011F0h] ; __vbaFreeObj
  loc_0041E1E8: ret
  loc_0041E1E9: mov ecx, var_10
  loc_0041E1EC: mov eax, var_20
  loc_0041E1EF: pop edi
  loc_0041E1F0: pop esi
  loc_0041E1F1: mov fs:[00000000h], ecx
  loc_0041E1F8: pop ebx
  loc_0041E1F9: mov esp, ebp
  loc_0041E1FB: pop ebp
  loc_0041E1FC: retn 0004h
End Sub

Private Sub Proc_2_3_41E210() '41E210
  loc_0041E210: push ebp
  loc_0041E211: mov ebp, esp
  loc_0041E213: sub esp, 00000008h
  loc_0041E216: push 00401AA6h ; __vbaExceptHandler
  loc_0041E21B: mov eax, fs:[00000000h]
  loc_0041E221: push eax
  loc_0041E222: mov fs:[00000000h], esp
  loc_0041E229: sub esp, 00000028h
  loc_0041E22C: push ebx
  loc_0041E22D: push esi
  loc_0041E22E: push edi
  loc_0041E22F: mov var_8, esp
  loc_0041E232: mov var_4, 00401828h
  loc_0041E239: mov esi, arg_8
  loc_0041E23C: xor eax, eax
  loc_0041E23E: mov var_14, eax
  loc_0041E241: mov var_24, eax
  loc_0041E244: lea eax, var_34
  loc_0041E247: lea ecx, var_24
  loc_0041E24A: push eax
  loc_0041E24B: push ecx
  loc_0041E24C: mov var_2C, esi
  loc_0041E24F: mov var_34, 00004008h
  loc_0041E256: call [004010A4h] ; rtcTrimVar
  loc_0041E25C: lea edx, var_24
  loc_0041E25F: push edx
  loc_0041E260: call [00401030h] ; __vbaStrVarMove
  loc_0041E266: mov edi, [004011D0h] ; __vbaStrMove
  loc_0041E26C: mov edx, eax
  loc_0041E26E: mov ecx, esi
  loc_0041E270: call edi
  loc_0041E272: lea ecx, var_24
  loc_0041E275: call [00401020h] ; __vbaFreeVar
  loc_0041E27B: mov ebx, [00401178h] ; __vbaStrCopy
  loc_0041E281: mov edx, 00408088h
  loc_0041E286: lea ecx, var_14
  loc_0041E289: call ebx
  loc_0041E28B: lea eax, var_14
  loc_0041E28E: push eax
  loc_0041E28F: push esi
  loc_0041E290: call 0041E320h
  loc_0041E295: mov edx, eax
  loc_0041E297: mov ecx, esi
  loc_0041E299: call edi
  loc_0041E29B: lea ecx, var_14
  loc_0041E29E: call [004011F4h] ; __vbaFreeStr
  loc_0041E2A4: mov edx, 00408090h
  loc_0041E2A9: lea ecx, var_14
  loc_0041E2AC: call ebx
  loc_0041E2AE: lea ecx, var_14
  loc_0041E2B1: push ecx
  loc_0041E2B2: push esi
  loc_0041E2B3: call 0041E320h
  loc_0041E2B8: mov edx, eax
  loc_0041E2BA: mov ecx, esi
  loc_0041E2BC: call edi
  loc_0041E2BE: lea ecx, var_14
  loc_0041E2C1: call [004011F4h] ; __vbaFreeStr
  loc_0041E2C7: mov edx, 00408088h
  loc_0041E2CC: lea ecx, var_14
  loc_0041E2CF: call ebx
  loc_0041E2D1: lea edx, var_14
  loc_0041E2D4: push edx
  loc_0041E2D5: push esi
  loc_0041E2D6: call 0041E320h
  loc_0041E2DB: mov edx, eax
  loc_0041E2DD: mov ecx, esi
  loc_0041E2DF: call edi
  loc_0041E2E1: lea ecx, var_14
  loc_0041E2E4: call [004011F4h] ; __vbaFreeStr
  loc_0041E2EA: push 0041E305h
  loc_0041E2EF: jmp 0041E304h
  loc_0041E2F1: lea ecx, var_14
  loc_0041E2F4: call [004011F4h] ; __vbaFreeStr
  loc_0041E2FA: lea ecx, var_24
  loc_0041E2FD: call [00401020h] ; __vbaFreeVar
  loc_0041E303: ret
  loc_0041E304: ret
  loc_0041E305: mov ecx, var_10
  loc_0041E308: pop edi
  loc_0041E309: pop esi
  loc_0041E30A: mov fs:[00000000h], ecx
  loc_0041E311: pop ebx
  loc_0041E312: mov esp, ebp
  loc_0041E314: pop ebp
  loc_0041E315: retn 0004h
End Sub

Private Sub Proc_2_4_41E320(arg_C) '41E320
  loc_0041E320: push ebp
  loc_0041E321: mov ebp, esp
  loc_0041E323: sub esp, 0000000Ch
  loc_0041E326: push 00401AA6h ; __vbaExceptHandler
  loc_0041E32B: mov eax, fs:[00000000h]
  loc_0041E331: push eax
  loc_0041E332: mov fs:[00000000h], esp
  loc_0041E339: sub esp, 00000030h
  loc_0041E33C: push ebx
  loc_0041E33D: push esi
  loc_0041E33E: push edi
  loc_0041E33F: mov var_C, esp
  loc_0041E342: mov var_8, 00401838h
  loc_0041E349: mov esi, arg_8
  loc_0041E34C: mov ecx, arg_C
  loc_0041E34F: push 00000001h
  loc_0041E351: xor edi, edi
  loc_0041E353: mov eax, [esi]
  loc_0041E355: mov edx, [ecx]
  loc_0041E357: push eax
  loc_0041E358: push edx
  loc_0041E359: push 00000001h
  loc_0041E35B: mov var_18, edi
  loc_0041E35E: mov var_2C, edi
  loc_0041E361: mov var_3C, edi
  loc_0041E364: call [0040116Ch] ; __vbaInStr
  loc_0041E36A: cmp eax, edi
  loc_0041E36C: jz 0041E3B1h
  loc_0041E36E: sub eax, 00000001h
  loc_0041E371: lea ecx, var_2C
  loc_0041E374: jo 0041E3F3h
  loc_0041E376: push eax
  loc_0041E377: lea eax, var_3C
  loc_0041E37A: push eax
  loc_0041E37B: push ecx
  loc_0041E37C: mov var_34, esi
  loc_0041E37F: mov var_3C, 00004008h
  loc_0041E386: call [004011C4h] ; rtcLeftCharVar
  loc_0041E38C: lea edx, var_2C
  loc_0041E38F: push edx
  loc_0041E390: call [00401030h] ; __vbaStrVarMove
  loc_0041E396: mov edx, eax
  loc_0041E398: lea ecx, var_18
  loc_0041E39B: call [004011D0h] ; __vbaStrMove
  loc_0041E3A1: lea ecx, var_2C
  loc_0041E3A4: call [00401020h] ; __vbaFreeVar
  loc_0041E3AA: push 0041E3DDh
  loc_0041E3AF: jmp 0041E3DCh
  loc_0041E3B1: mov edx, [esi]
  loc_0041E3B3: lea ecx, var_18
  loc_0041E3B6: call [00401178h] ; __vbaStrCopy
  loc_0041E3BC: push 0041E3DDh
  loc_0041E3C1: jmp 0041E3DCh
  loc_0041E3C3: test var_4, 04h
  loc_0041E3C7: jz 0041E3D2h
  loc_0041E3C9: lea ecx, var_18
  loc_0041E3CC: call [004011F4h] ; __vbaFreeStr
  loc_0041E3D2: lea ecx, var_2C
  loc_0041E3D5: call [00401020h] ; __vbaFreeVar
  loc_0041E3DB: ret
  loc_0041E3DC: ret
  loc_0041E3DD: mov ecx, var_14
  loc_0041E3E0: mov eax, var_18
  loc_0041E3E3: pop edi
  loc_0041E3E4: pop esi
  loc_0041E3E5: mov fs:[00000000h], ecx
  loc_0041E3EC: pop ebx
  loc_0041E3ED: mov esp, ebp
  loc_0041E3EF: pop ebp
  loc_0041E3F0: retn 0008h
End Sub

Private Function Proc_2_5_41E400(arg_C, arg_10, arg_14, arg_18) '41E400
  loc_0041E400: push ebp
  loc_0041E401: mov ebp, esp
  loc_0041E403: sub esp, 00000018h
  loc_0041E406: push 00401AA6h ; __vbaExceptHandler
  loc_0041E40B: mov eax, fs:[00000000h]
  loc_0041E411: push eax
  loc_0041E412: mov fs:[00000000h], esp
  loc_0041E419: mov eax, 000001B4h
  loc_0041E41E: call 00401AA0h ; __vbaChkstk
  loc_0041E423: push ebx
  loc_0041E424: push esi
  loc_0041E425: push edi
  loc_0041E426: mov var_18, esp
  loc_0041E429: mov var_14, 00401848h
  loc_0041E430: mov var_10, 00000000h
  loc_0041E437: mov var_C, 00000000h
  loc_0041E43E: mov var_4, 00000001h
  loc_0041E445: mov var_4, 00000002h
  loc_0041E44C: mov var_40, 80020004h
  loc_0041E453: mov var_48, 0000000Ah
  loc_0041E45A: lea eax, var_48
  loc_0041E45D: push eax
  loc_0041E45E: call [00401164h] ; rtcFreeFile
  loc_0041E464: movsx ecx, ax
  loc_0041E467: mov var_24, ecx
  loc_0041E46A: lea ecx, var_48
  loc_0041E46D: call [00401020h] ; __vbaFreeVar
  loc_0041E473: mov var_4, 00000003h
  loc_0041E47A: push FFFFFFFFh
  loc_0041E47C: call [0040107Ch] ; __vbaOnError
  loc_0041E482: mov var_4, 00000004h
  loc_0041E489: push 004080F8h ; "C:\ProbeData\HPIB_Bus_Errors.txt"
  loc_0041E48E: mov ecx, var_24
  loc_0041E491: call [004010ECh] ; __vbaI2I4
  loc_0041E497: push eax
  loc_0041E498: push FFFFFFFFh
  loc_0041E49A: push 00000008h
  loc_0041E49C: call [0040115Ch] ; __vbaFileOpen
  loc_0041E4A2: mov var_4, 00000005h
  loc_0041E4A9: call [00401190h] ; rtcErrObj
  loc_0041E4AF: push eax
  loc_0041E4B0: lea edx, var_38
  loc_0041E4B3: push edx
  loc_0041E4B4: call [00401080h] ; __vbaObjSet
  loc_0041E4BA: mov var_1B0, eax
  loc_0041E4C0: lea eax, var_1AC
  loc_0041E4C6: push eax
  loc_0041E4C7: mov ecx, var_1B0
  loc_0041E4CD: mov edx, [ecx]
  loc_0041E4CF: mov eax, var_1B0
  loc_0041E4D5: push eax
  loc_0041E4D6: call [edx+0000001Ch]
  loc_0041E4D9: fnclex
  loc_0041E4DB: mov var_1B4, eax
  loc_0041E4E1: cmp var_1B4, 00000000h
  loc_0041E4E8: jge 0041E50Dh
  loc_0041E4EA: push 0000001Ch
  loc_0041E4EC: push 00406F64h
  loc_0041E4F1: mov ecx, var_1B0
  loc_0041E4F7: push ecx
  loc_0041E4F8: mov edx, var_1B4
  loc_0041E4FE: push edx
  loc_0041E4FF: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041E505: mov var_1D0, eax
  loc_0041E50B: jmp 0041E517h
  loc_0041E50D: mov var_1D0, 00000000h
  loc_0041E517: xor eax, eax
  loc_0041E519: cmp var_1AC, 00000000h
  loc_0041E520: setnz al
  loc_0041E523: neg eax
  loc_0041E525: mov var_1B8, ax
  loc_0041E52C: lea ecx, var_38
  loc_0041E52F: call [004011F0h] ; __vbaFreeObj
  loc_0041E535: movsx ecx, var_1B8
  loc_0041E53C: test ecx, ecx
  loc_0041E53E: jz 0041E57Eh
  loc_0041E540: mov var_4, 00000006h
  loc_0041E547: call [00401190h] ; rtcErrObj
  loc_0041E54D: push eax
  loc_0041E54E: lea edx, var_38
  loc_0041E551: push edx
  loc_0041E552: call [00401080h] ; __vbaObjSet
  loc_0041E558: mov var_1D4, eax
  loc_0041E55E: mov eax, var_1D4
  loc_0041E564: mov ecx, [eax]
  loc_0041E566: mov edx, var_1D4
  loc_0041E56C: push edx
  loc_0041E56D: call [ecx+00000048h]
  loc_0041E570: lea ecx, var_38
  loc_0041E573: call [004011F0h] ; __vbaFreeObj
  loc_0041E579: jmp 0041E7D2h
  loc_0041E57E: mov var_4, 00000009h
  loc_0041E585: lea eax, var_48
  loc_0041E588: push eax
  loc_0041E589: call [004011E4h] ; rtcGetPresentDate
  loc_0041E58F: mov var_120, 00408140h ; "General Date"
  loc_0041E599: mov var_128, 00000008h
  loc_0041E5A3: lea edx, var_128
  loc_0041E5A9: lea ecx, var_58
  loc_0041E5AC: call [004011B4h] ; __vbaVarDup
  loc_0041E5B2: push 00000001h
  loc_0041E5B4: push 00000001h
  loc_0041E5B6: lea ecx, var_58
  loc_0041E5B9: push ecx
  loc_0041E5BA: lea edx, var_48
  loc_0041E5BD: push edx
  loc_0041E5BE: lea eax, var_68
  loc_0041E5C1: push eax
  loc_0041E5C2: call [00401054h] ; rtcVarFromFormatVar
  loc_0041E5C8: mov ecx, arg_18
  loc_0041E5CB: mov edx, [ecx]
  loc_0041E5CD: push edx
  loc_0041E5CE: call [00401018h] ; __vbaStrI4
  loc_0041E5D4: mov var_D0, eax
  loc_0041E5DA: mov var_D8, 00000008h
  loc_0041E5E4: lea eax, var_D8
  loc_0041E5EA: push eax
  loc_0041E5EB: lea ecx, var_E8
  loc_0041E5F1: push ecx
  loc_0041E5F2: call [004010A4h] ; rtcTrimVar
  loc_0041E5F8: mov var_130, 00408160h
  loc_0041E602: mov var_138, 00000008h
  loc_0041E60C: mov edx, arg_C
  loc_0041E60F: mov eax, [edx]
  loc_0041E611: mov var_140, eax
  loc_0041E617: mov var_148, 00000008h
  loc_0041E621: mov var_150, 00408160h
  loc_0041E62B: mov var_158, 00000008h
  loc_0041E635: mov ecx, arg_10
  loc_0041E638: mov edx, [ecx]
  loc_0041E63A: mov var_160, edx
  loc_0041E640: mov var_168, 00000008h
  loc_0041E64A: mov var_170, 00408160h
  loc_0041E654: mov var_178, 00000008h
  loc_0041E65E: mov var_180, 00407F68h ; "Error Number:"
  loc_0041E668: mov var_188, 00000008h
  loc_0041E672: mov var_190, 00408160h
  loc_0041E67C: mov var_198, 00000008h
  loc_0041E686: mov eax, arg_14
  loc_0041E689: mov ecx, [eax]
  loc_0041E68B: mov var_1A0, ecx
  loc_0041E691: mov var_1A8, 00000008h
  loc_0041E69B: lea edx, var_68
  loc_0041E69E: push edx
  loc_0041E69F: lea eax, var_138
  loc_0041E6A5: push eax
  loc_0041E6A6: lea ecx, var_78
  loc_0041E6A9: push ecx
  loc_0041E6AA: call [004011ACh] ; __vbaVarAdd
  loc_0041E6B0: push eax
  loc_0041E6B1: lea edx, var_148
  loc_0041E6B7: push edx
  loc_0041E6B8: lea eax, var_88
  loc_0041E6BE: push eax
  loc_0041E6BF: call [004011ACh] ; __vbaVarAdd
  loc_0041E6C5: push eax
  loc_0041E6C6: lea ecx, var_158
  loc_0041E6CC: push ecx
  loc_0041E6CD: lea edx, var_98
  loc_0041E6D3: push edx
  loc_0041E6D4: call [004011ACh] ; __vbaVarAdd
  loc_0041E6DA: push eax
  loc_0041E6DB: lea eax, var_168
  loc_0041E6E1: push eax
  loc_0041E6E2: lea ecx, var_A8
  loc_0041E6E8: push ecx
  loc_0041E6E9: call [004011ACh] ; __vbaVarAdd
  loc_0041E6EF: push eax
  loc_0041E6F0: lea edx, var_178
  loc_0041E6F6: push edx
  loc_0041E6F7: lea eax, var_B8
  loc_0041E6FD: push eax
  loc_0041E6FE: call [004011ACh] ; __vbaVarAdd
  loc_0041E704: push eax
  loc_0041E705: lea ecx, var_188
  loc_0041E70B: push ecx
  loc_0041E70C: lea edx, var_C8
  loc_0041E712: push edx
  loc_0041E713: call [004011ACh] ; __vbaVarAdd
  loc_0041E719: push eax
  loc_0041E71A: lea eax, var_E8
  loc_0041E720: push eax
  loc_0041E721: lea ecx, var_F8
  loc_0041E727: push ecx
  loc_0041E728: call [004011ACh] ; __vbaVarAdd
  loc_0041E72E: push eax
  loc_0041E72F: lea edx, var_198
  loc_0041E735: push edx
  loc_0041E736: lea eax, var_108
  loc_0041E73C: push eax
  loc_0041E73D: call [004011ACh] ; __vbaVarAdd
  loc_0041E743: push eax
  loc_0041E744: lea ecx, var_1A8
  loc_0041E74A: push ecx
  loc_0041E74B: lea edx, var_118
  loc_0041E751: push edx
  loc_0041E752: call [004011ACh] ; __vbaVarAdd
  loc_0041E758: push eax
  loc_0041E759: mov ecx, var_24
  loc_0041E75C: call [004010ECh] ; __vbaI2I4
  loc_0041E762: push eax
  loc_0041E763: push 00407F88h
  loc_0041E768: call [00401128h] ; __vbaPrintFile
  loc_0041E76E: add esp, 0000000Ch
  loc_0041E771: lea eax, var_118
  loc_0041E777: push eax
  loc_0041E778: lea ecx, var_108
  loc_0041E77E: push ecx
  loc_0041E77F: lea edx, var_F8
  loc_0041E785: push edx
  loc_0041E786: lea eax, var_E8
  loc_0041E78C: push eax
  loc_0041E78D: lea ecx, var_C8
  loc_0041E793: push ecx
  loc_0041E794: lea edx, var_D8
  loc_0041E79A: push edx
  loc_0041E79B: lea eax, var_B8
  loc_0041E7A1: push eax
  loc_0041E7A2: lea ecx, var_A8
  loc_0041E7A8: push ecx
  loc_0041E7A9: lea edx, var_98
  loc_0041E7AF: push edx
  loc_0041E7B0: lea eax, var_88
  loc_0041E7B6: push eax
  loc_0041E7B7: lea ecx, var_78
  loc_0041E7BA: push ecx
  loc_0041E7BB: lea edx, var_68
  loc_0041E7BE: push edx
  loc_0041E7BF: lea eax, var_58
  loc_0041E7C2: push eax
  loc_0041E7C3: lea ecx, var_48
  loc_0041E7C6: push ecx
  loc_0041E7C7: push 0000000Eh
  loc_0041E7C9: call [00401038h] ; __vbaFreeVarList
  loc_0041E7CF: add esp, 0000003Ch
  loc_0041E7D2: mov var_4, 0000000Bh
  loc_0041E7D9: mov ecx, var_24
  loc_0041E7DC: call [004010ECh] ; __vbaI2I4
  loc_0041E7E2: push eax
  loc_0041E7E3: call [004010CCh] ; __vbaFileClose
  loc_0041E7E9: push 0041E86Fh
  loc_0041E7EE: jmp 0041E86Eh
  loc_0041E7F0: mov edx, var_10
  loc_0041E7F3: and edx, 00000004h
  loc_0041E7F6: test edx, edx
  loc_0041E7F8: jz 0041E803h
  loc_0041E7FA: lea ecx, var_34
  loc_0041E7FD: call [00401020h] ; __vbaFreeVar
  loc_0041E803: lea ecx, var_38
  loc_0041E806: call [004011F0h] ; __vbaFreeObj
  loc_0041E80C: lea eax, var_118
  loc_0041E812: push eax
  loc_0041E813: lea ecx, var_108
  loc_0041E819: push ecx
  loc_0041E81A: lea edx, var_F8
  loc_0041E820: push edx
  loc_0041E821: lea eax, var_E8
  loc_0041E827: push eax
  loc_0041E828: lea ecx, var_D8
  loc_0041E82E: push ecx
  loc_0041E82F: lea edx, var_C8
  loc_0041E835: push edx
  loc_0041E836: lea eax, var_B8
  loc_0041E83C: push eax
  loc_0041E83D: lea ecx, var_A8
  loc_0041E843: push ecx
  loc_0041E844: lea edx, var_98
  loc_0041E84A: push edx
  loc_0041E84B: lea eax, var_88
  loc_0041E851: push eax
  loc_0041E852: lea ecx, var_78
  loc_0041E855: push ecx
  loc_0041E856: lea edx, var_68
  loc_0041E859: push edx
  loc_0041E85A: lea eax, var_58
  loc_0041E85D: push eax
  loc_0041E85E: lea ecx, var_48
  loc_0041E861: push ecx
  loc_0041E862: push 0000000Eh
  loc_0041E864: call [00401038h] ; __vbaFreeVarList
  loc_0041E86A: add esp, 0000003Ch
  loc_0041E86D: ret
  loc_0041E86E: ret
  loc_0041E86F: mov edx, arg_8
  loc_0041E872: mov eax, var_34
  loc_0041E875: mov [edx], eax
  loc_0041E877: mov ecx, var_30
  loc_0041E87A: mov [edx+00000004h], ecx
  loc_0041E87D: mov eax, var_2C
  loc_0041E880: mov [edx+00000008h], eax
  loc_0041E883: mov ecx, var_28
  loc_0041E886: mov [edx+0000000Ch], ecx
  loc_0041E889: mov eax, arg_8
  loc_0041E88C: mov ecx, var_20
  loc_0041E88F: mov fs:[00000000h], ecx
  loc_0041E896: pop edi
  loc_0041E897: pop esi
  loc_0041E898: pop ebx
  loc_0041E899: mov esp, ebp
  loc_0041E89B: pop ebp
  loc_0041E89C: retn 0014h
End Function

Private Sub Proc_2_6_41E8A0() '41E8A0
  loc_0041E8A0: push ebp
  loc_0041E8A1: mov ebp, esp
  loc_0041E8A3: sub esp, 00000014h
  loc_0041E8A6: push 00401AA6h ; __vbaExceptHandler
  loc_0041E8AB: mov eax, fs:[00000000h]
  loc_0041E8B1: push eax
  loc_0041E8B2: mov fs:[00000000h], esp
  loc_0041E8B9: sub esp, 00000090h
  loc_0041E8BF: push ebx
  loc_0041E8C0: push esi
  loc_0041E8C1: push edi
  loc_0041E8C2: mov var_14, esp
  loc_0041E8C5: mov var_10, 00401898h
  loc_0041E8CC: xor edi, edi
  loc_0041E8CE: mov var_C, edi
  loc_0041E8D1: mov var_8, edi
  loc_0041E8D4: mov var_20, edi
  loc_0041E8D7: mov var_24, edi
  loc_0041E8DA: mov var_34, edi
  loc_0041E8DD: mov var_44, edi
  loc_0041E8E0: mov var_54, edi
  loc_0041E8E3: mov var_64, edi
  loc_0041E8E6: mov var_74, edi
  loc_0041E8E9: mov var_84, edi
  loc_0041E8EF: push 00407DC4h
  loc_0041E8F4: mov ebx, [00401110h] ; __vbaNew
  loc_0041E8FA: call ebx
  loc_0041E8FC: push eax
  loc_0041E8FD: push 00423024h
  loc_0041E902: call [00401080h] ; __vbaObjSet
  loc_0041E908: mov eax, [00423024h]
  loc_0041E90D: mov ecx, [eax]
  loc_0041E90F: push 00404F24h ; "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=P:\ProberMaster.mdb;User ID=;Password="
  loc_0041E914: push eax
  loc_0041E915: call [ecx+00000024h]
  loc_0041E918: fnclex
  loc_0041E91A: cmp eax, edi
  loc_0041E91C: jge 0041E937h
  loc_0041E91E: push 00000024h
  loc_0041E920: push 00406924h
  loc_0041E925: mov edx, [00423024h]
  loc_0041E92B: push edx
  loc_0041E92C: push eax
  loc_0041E92D: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041E933: call __vbaHresultCheckObj
  loc_0041E935: jmp 0041E93Dh
  loc_0041E937: mov esi, [0040105Ch] ; __vbaHresultCheckObj
  loc_0041E93D: mov eax, [00423024h]
  loc_0041E942: mov ecx, [eax]
  loc_0041E944: push 00000003h
  loc_0041E946: push eax
  loc_0041E947: call [ecx+0000007Ch]
  loc_0041E94A: fnclex
  loc_0041E94C: cmp eax, edi
  loc_0041E94E: jge 0041E961h
  loc_0041E950: push 0000007Ch
  loc_0041E952: push 00406924h
  loc_0041E957: mov edx, [00423024h]
  loc_0041E95D: push edx
  loc_0041E95E: push eax
  loc_0041E95F: call __vbaHresultCheckObj
  loc_0041E961: push 00000001h
  loc_0041E963: call [0040107Ch] ; __vbaOnError
  loc_0041E969: mov eax, [00423024h]
  loc_0041E96E: mov ecx, [eax]
  loc_0041E970: push FFFFFFFFh
  loc_0041E972: push 00406B58h
  loc_0041E977: push 00406B58h
  loc_0041E97C: push 00406B58h
  loc_0041E981: push eax
  loc_0041E982: call [ecx+00000050h]
  loc_0041E985: fnclex
  loc_0041E987: cmp eax, edi
  loc_0041E989: jge 0041E99Ch
  loc_0041E98B: push 00000050h
  loc_0041E98D: push 00406924h
  loc_0041E992: mov edx, [00423024h]
  loc_0041E998: push edx
  loc_0041E999: push eax
  loc_0041E99A: call __vbaHresultCheckObj
  loc_0041E99C: push edi
  loc_0041E99D: call [0040107Ch] ; __vbaOnError
  loc_0041E9A3: mov [0042302Ch], FFFFFFh
  loc_0041E9AC: push 00407DC4h
  loc_0041E9B1: call ebx
  loc_0041E9B3: push eax
  loc_0041E9B4: push 00423028h
  loc_0041E9B9: call [00401080h] ; __vbaObjSet
  loc_0041E9BF: mov eax, [00423028h]
  loc_0041E9C4: mov ecx, [eax]
  loc_0041E9C6: push 00405024h ; "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=P:\LampElectricalProbeData.mdb;User ID=;Password="
  loc_0041E9CB: push eax
  loc_0041E9CC: call [ecx+00000024h]
  loc_0041E9CF: fnclex
  loc_0041E9D1: cmp eax, edi
  loc_0041E9D3: jge 0041E9E6h
  loc_0041E9D5: push 00000024h
  loc_0041E9D7: push 00406924h
  loc_0041E9DC: mov edx, [00423028h]
  loc_0041E9E2: push edx
  loc_0041E9E3: push eax
  loc_0041E9E4: call __vbaHresultCheckObj
  loc_0041E9E6: mov eax, [00423028h]
  loc_0041E9EB: mov ecx, [eax]
  loc_0041E9ED: push 00000003h
  loc_0041E9EF: push eax
  loc_0041E9F0: call [ecx+00000074h]
  loc_0041E9F3: fnclex
  loc_0041E9F5: cmp eax, edi
  loc_0041E9F7: jge 0041EA0Ah
  loc_0041E9F9: push 00000074h
  loc_0041E9FB: push 00406924h
  loc_0041EA00: mov edx, [00423028h]
  loc_0041EA06: push edx
  loc_0041EA07: push eax
  loc_0041EA08: call __vbaHresultCheckObj
  loc_0041EA0A: mov eax, [00423028h]
  loc_0041EA0F: mov ecx, [eax]
  loc_0041EA11: push 00000003h
  loc_0041EA13: push eax
  loc_0041EA14: call [ecx+0000007Ch]
  loc_0041EA17: fnclex
  loc_0041EA19: cmp eax, edi
  loc_0041EA1B: jge 0041EA2Eh
  loc_0041EA1D: push 0000007Ch
  loc_0041EA1F: push 00406924h
  loc_0041EA24: mov edx, [00423028h]
  loc_0041EA2A: push edx
  loc_0041EA2B: push eax
  loc_0041EA2C: call __vbaHresultCheckObj
  loc_0041EA2E: push 00000002h
  loc_0041EA30: mov ebx, [0040107Ch] ; __vbaOnError
  loc_0041EA36: call ebx
  loc_0041EA38: mov eax, [00423028h]
  loc_0041EA3D: mov ecx, [eax]
  loc_0041EA3F: push FFFFFFFFh
  loc_0041EA41: push 00406B58h
  loc_0041EA46: push 00406B58h
  loc_0041EA4B: push 00406B58h
  loc_0041EA50: push eax
  loc_0041EA51: call [ecx+00000050h]
  loc_0041EA54: fnclex
  loc_0041EA56: cmp eax, edi
  loc_0041EA58: jge 0041EA6Bh
  loc_0041EA5A: push 00000050h
  loc_0041EA5C: push 00406924h
  loc_0041EA61: mov edx, [00423028h]
  loc_0041EA67: push edx
  loc_0041EA68: push eax
  loc_0041EA69: call __vbaHresultCheckObj
  loc_0041EA6B: push edi
  loc_0041EA6C: call ebx
  loc_0041EA6E: mov [0042302Eh], FFFFFFh
  loc_0041EA77: cmp [00423010h], edi
  loc_0041EA7D: jnz 0041EA8Fh
  loc_0041EA7F: push 00423010h
  loc_0041EA84: push 004025D8h
  loc_0041EA89: call [00401168h] ; __vbaNew2
  loc_0041EA8F: mov esi, [00423010h]
  loc_0041EA95: mov eax, 80020004h
  loc_0041EA9A: mov ecx, 0000000Ah
  loc_0041EA9F: mov edx, eax
  loc_0041EAA1: mov var_6C, edx
  loc_0041EAA4: mov var_74, ecx
  loc_0041EAA7: mov edi, [esi]
  loc_0041EAA9: sub esp, 00000010h
  loc_0041EAAC: mov ebx, esp
  loc_0041EAAE: mov [ebx], ecx
  loc_0041EAB0: mov ecx, var_80
  loc_0041EAB3: mov [ebx+00000004h], ecx
  loc_0041EAB6: mov [ebx+00000008h], eax
  loc_0041EAB9: mov eax, var_78
  loc_0041EABC: mov [ebx+0000000Ch], eax
  loc_0041EABF: sub esp, 00000010h
  loc_0041EAC2: mov ecx, esp
  loc_0041EAC4: mov eax, var_74
  loc_0041EAC7: mov [ecx], eax
  loc_0041EAC9: mov eax, var_70
  loc_0041EACC: mov [ecx+00000004h], eax
  loc_0041EACF: mov [ecx+00000008h], edx
  loc_0041EAD2: mov edx, var_68
  loc_0041EAD5: mov [ecx+0000000Ch], edx
  loc_0041EAD8: push esi
  loc_0041EAD9: call [edi+000002B0h]
  loc_0041EADF: fnclex
  loc_0041EAE1: test eax, eax
  loc_0041EAE3: jge 0041EC85h
  loc_0041EAE9: push 000002B0h
  loc_0041EAEE: push 00405120h
  loc_0041EAF3: push esi
  loc_0041EAF4: push eax
  loc_0041EAF5: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041EAFB: call [00401074h] ; __vbaExitProc
  loc_0041EB01: push 0041ECC1h
  loc_0041EB06: jmp 0041ECC0h
  loc_0041EB0B: mov eax, 80020004h
  loc_0041EB10: mov var_5C, eax
  loc_0041EB13: mov ecx, 0000000Ah
  loc_0041EB18: mov var_64, ecx
  loc_0041EB1B: mov var_4C, eax
  loc_0041EB1E: mov var_54, ecx
  loc_0041EB21: mov var_6C, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041EB28: mov edi, 00000008h
  loc_0041EB2D: mov var_74, edi
  loc_0041EB30: lea edx, var_74
  loc_0041EB33: lea ecx, var_44
  loc_0041EB36: call [004011B4h] ; __vbaVarDup
  loc_0041EB3C: push 004081C8h ; "An attempt to make a connection to the Master Prober database failed! Please alert an engineer."
  loc_0041EB41: push 004054D8h ; vbCrLf
  loc_0041EB46: mov esi, [00401050h] ; __vbaStrCat
  loc_0041EB4C: call __vbaStrCat
  loc_0041EB4E: mov edx, eax
  loc_0041EB50: lea ecx, var_20
  loc_0041EB53: call [004011D0h] ; __vbaStrMove
  loc_0041EB59: push eax
  loc_0041EB5A: push 0040828Ch ; "Without this connection the prober cannot run."
  loc_0041EB5F: call __vbaStrCat
  loc_0041EB61: mov var_2C, eax
  loc_0041EB64: mov var_34, edi
  loc_0041EB67: lea eax, var_64
  loc_0041EB6A: push eax
  loc_0041EB6B: lea ecx, var_54
  loc_0041EB6E: push ecx
  loc_0041EB6F: lea edx, var_44
  loc_0041EB72: push edx
  loc_0041EB73: push 00000010h
  loc_0041EB75: lea eax, var_34
  loc_0041EB78: push eax
  loc_0041EB79: call [00401084h] ; rtcMsgBox
  loc_0041EB7F: lea ecx, var_20
  loc_0041EB82: call [004011F4h] ; __vbaFreeStr
  loc_0041EB88: lea ecx, var_64
  loc_0041EB8B: push ecx
  loc_0041EB8C: lea edx, var_54
  loc_0041EB8F: push edx
  loc_0041EB90: lea eax, var_44
  loc_0041EB93: push eax
  loc_0041EB94: lea ecx, var_34
  loc_0041EB97: push ecx
  loc_0041EB98: push 00000004h
  loc_0041EB9A: call [00401038h] ; __vbaFreeVarList
  loc_0041EBA0: add esp, 00000014h
  loc_0041EBA3: call [00401190h] ; rtcErrObj
  loc_0041EBA9: push eax
  loc_0041EBAA: lea edx, var_24
  loc_0041EBAD: push edx
  loc_0041EBAE: call [00401080h] ; __vbaObjSet
  loc_0041EBB4: mov ecx, [eax]
  loc_0041EBB6: push eax
  loc_0041EBB7: call [ecx+00000048h]
  loc_0041EBBA: lea ecx, var_24
  loc_0041EBBD: call [004011F0h] ; __vbaFreeObj
  loc_0041EBC3: call 0041ECE0h
  loc_0041EBC8: mov eax, 80020004h
  loc_0041EBCD: mov var_5C, eax
  loc_0041EBD0: mov ecx, 0000000Ah
  loc_0041EBD5: mov var_64, ecx
  loc_0041EBD8: mov var_4C, eax
  loc_0041EBDB: mov var_54, ecx
  loc_0041EBDE: mov var_6C, 004050E8h ; "IMT LampElectrical Probing"
  loc_0041EBE5: mov edi, 00000008h
  loc_0041EBEA: mov var_74, edi
  loc_0041EBED: lea edx, var_74
  loc_0041EBF0: lea ecx, var_44
  loc_0041EBF3: call [004011B4h] ; __vbaVarDup
  loc_0041EBF9: push 004082F0h ; "An attempt to make a connection to the LampElectrical database failed! Please alert an engineer."
  loc_0041EBFE: push 004054D8h ; vbCrLf
  loc_0041EC03: mov esi, [00401050h] ; __vbaStrCat
  loc_0041EC09: call __vbaStrCat
  loc_0041EC0B: mov edx, eax
  loc_0041EC0D: lea ecx, var_20
  loc_0041EC10: call [004011D0h] ; __vbaStrMove
  loc_0041EC16: push eax
  loc_0041EC17: push 0040828Ch ; "Without this connection the prober cannot run."
  loc_0041EC1C: call __vbaStrCat
  loc_0041EC1E: mov var_2C, eax
  loc_0041EC21: mov var_34, edi
  loc_0041EC24: lea edx, var_64
  loc_0041EC27: push edx
  loc_0041EC28: lea eax, var_54
  loc_0041EC2B: push eax
  loc_0041EC2C: lea ecx, var_44
  loc_0041EC2F: push ecx
  loc_0041EC30: push 00000010h
  loc_0041EC32: lea edx, var_34
  loc_0041EC35: push edx
  loc_0041EC36: call [00401084h] ; rtcMsgBox
  loc_0041EC3C: lea ecx, var_20
  loc_0041EC3F: call [004011F4h] ; __vbaFreeStr
  loc_0041EC45: lea eax, var_64
  loc_0041EC48: push eax
  loc_0041EC49: lea ecx, var_54
  loc_0041EC4C: push ecx
  loc_0041EC4D: lea edx, var_44
  loc_0041EC50: push edx
  loc_0041EC51: lea eax, var_34
  loc_0041EC54: push eax
  loc_0041EC55: push 00000004h
  loc_0041EC57: call [00401038h] ; __vbaFreeVarList
  loc_0041EC5D: add esp, 00000014h
  loc_0041EC60: call [00401190h] ; rtcErrObj
  loc_0041EC66: push eax
  loc_0041EC67: lea ecx, var_24
  loc_0041EC6A: push ecx
  loc_0041EC6B: call [00401080h] ; __vbaObjSet
  loc_0041EC71: mov edx, [eax]
  loc_0041EC73: push eax
  loc_0041EC74: call [edx+00000048h]
  loc_0041EC77: lea ecx, var_24
  loc_0041EC7A: call [004011F0h] ; __vbaFreeObj
  loc_0041EC80: call 0041ECE0h
  loc_0041EC85: call [00401074h] ; __vbaExitProc
  loc_0041EC8B: push 0041ECC1h
  loc_0041EC90: jmp 0041ECC0h
  loc_0041EC92: lea ecx, var_20
  loc_0041EC95: call [004011F4h] ; __vbaFreeStr
  loc_0041EC9B: lea ecx, var_24
  loc_0041EC9E: call [004011F0h] ; __vbaFreeObj
  loc_0041ECA4: lea eax, var_64
  loc_0041ECA7: push eax
  loc_0041ECA8: lea ecx, var_54
  loc_0041ECAB: push ecx
  loc_0041ECAC: lea edx, var_44
  loc_0041ECAF: push edx
  loc_0041ECB0: lea eax, var_34
  loc_0041ECB3: push eax
  loc_0041ECB4: push 00000004h
  loc_0041ECB6: call [00401038h] ; __vbaFreeVarList
  loc_0041ECBC: add esp, 00000014h
  loc_0041ECBF: ret
  loc_0041ECC0: ret
  loc_0041ECC1: mov ecx, var_1C
  loc_0041ECC4: mov fs:[00000000h], ecx
  loc_0041ECCB: pop edi
  loc_0041ECCC: pop esi
  loc_0041ECCD: pop ebx
  loc_0041ECCE: mov esp, ebp
  loc_0041ECD0: pop ebp
  loc_0041ECD1: ret
  loc_0041ECD2: nop
End Sub

Private Function Proc_2_7_41ECE0(arg_C, arg_10, arg_14) '41ECE0
  loc_0041ECE0: push ebp
  loc_0041ECE1: mov ebp, esp
  loc_0041ECE3: sub esp, 00000018h
  loc_0041ECE6: push 00401AA6h ; __vbaExceptHandler
  loc_0041ECEB: mov eax, fs:[00000000h]
  loc_0041ECF1: push eax
  loc_0041ECF2: mov fs:[00000000h], esp
  loc_0041ECF9: mov eax, 00000048h
  loc_0041ECFE: call 00401AA0h ; __vbaChkstk
  loc_0041ED03: push ebx
  loc_0041ED04: push esi
  loc_0041ED05: push edi
  loc_0041ED06: mov var_18, esp
  loc_0041ED09: mov var_14, 004018C8h
  loc_0041ED10: mov var_10, 00000000h
  loc_0041ED17: mov var_C, 00000000h
  loc_0041ED1E: mov var_4, 00000001h
  loc_0041ED25: mov var_4, 00000002h
  loc_0041ED2C: push 00000001h
  loc_0041ED2E: call [0040107Ch] ; __vbaOnError
  loc_0041ED34: mov var_4, 00000003h
  loc_0041ED3B: mov eax, [00423024h]
  loc_0041ED40: push eax
  loc_0041ED41: lea ecx, var_24
  loc_0041ED44: push ecx
  loc_0041ED45: call [00401094h] ; __vbaObjSetAddref
  loc_0041ED4B: lea edx, var_24
  loc_0041ED4E: mov var_2C, edx
  loc_0041ED51: mov var_34, 00004009h
  loc_0041ED58: lea eax, var_34
  loc_0041ED5B: push eax
  loc_0041ED5C: call [004010F0h] ; rtcIsObject
  loc_0041ED62: mov var_38, ax
  loc_0041ED66: push 00406B2Ch
  loc_0041ED6B: mov ecx, var_24
  loc_0041ED6E: push ecx
  loc_0041ED6F: call [004011D4h] ; __vbaCastObj
  loc_0041ED75: push eax
  loc_0041ED76: push 00423024h
  loc_0041ED7B: call [00401080h] ; __vbaObjSet
  loc_0041ED81: mov dx, var_38
  loc_0041ED85: mov var_40, dx
  loc_0041ED89: lea ecx, var_24
  loc_0041ED8C: call [004011F0h] ; __vbaFreeObj
  loc_0041ED92: movsx eax, var_40
  loc_0041ED96: test eax, eax
  loc_0041ED98: jz 0041EE5Dh
  loc_0041ED9E: mov var_4, 00000004h
  loc_0041EDA5: lea ecx, var_3C
  loc_0041EDA8: push ecx
  loc_0041EDA9: mov edx, [00423024h]
  loc_0041EDAF: mov eax, [edx]
  loc_0041EDB1: mov ecx, [00423024h]
  loc_0041EDB7: push ecx
  loc_0041EDB8: call [eax+00000088h]
  loc_0041EDBE: fnclex
  loc_0041EDC0: mov var_40, eax
  loc_0041EDC3: cmp var_40, 00000000h
  loc_0041EDC7: jge 0041EDE9h
  loc_0041EDC9: push 00000088h
  loc_0041EDCE: push 00406924h
  loc_0041EDD3: mov edx, [00423024h]
  loc_0041EDD9: push edx
  loc_0041EDDA: mov eax, var_40
  loc_0041EDDD: push eax
  loc_0041EDDE: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041EDE4: mov var_58, eax
  loc_0041EDE7: jmp 0041EDF0h
  loc_0041EDE9: mov var_58, 00000000h
  loc_0041EDF0: cmp var_3C, 00000001h
  loc_0041EDF4: jnz 0041EE3Dh
  loc_0041EDF6: mov var_4, 00000005h
  loc_0041EDFD: mov ecx, [00423024h]
  loc_0041EE03: mov edx, [ecx]
  loc_0041EE05: mov eax, [00423024h]
  loc_0041EE0A: push eax
  loc_0041EE0B: call [edx+0000003Ch]
  loc_0041EE0E: fnclex
  loc_0041EE10: mov var_40, eax
  loc_0041EE13: cmp var_40, 00000000h
  loc_0041EE17: jge 0041EE36h
  loc_0041EE19: push 0000003Ch
  loc_0041EE1B: push 00406924h
  loc_0041EE20: mov ecx, [00423024h]
  loc_0041EE26: push ecx
  loc_0041EE27: mov edx, var_40
  loc_0041EE2A: push edx
  loc_0041EE2B: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041EE31: mov var_5C, eax
  loc_0041EE34: jmp 0041EE3Dh
  loc_0041EE36: mov var_5C, 00000000h
  loc_0041EE3D: mov var_4, 00000007h
  loc_0041EE44: push 00406B2Ch
  loc_0041EE49: push 00000000h
  loc_0041EE4B: call [004011D4h] ; __vbaCastObj
  loc_0041EE51: push eax
  loc_0041EE52: push 00423024h
  loc_0041EE57: call [00401080h] ; __vbaObjSet
  loc_0041EE5D: mov var_4, 00000009h
  loc_0041EE64: mov eax, [00423028h]
  loc_0041EE69: push eax
  loc_0041EE6A: lea ecx, var_24
  loc_0041EE6D: push ecx
  loc_0041EE6E: call [00401094h] ; __vbaObjSetAddref
  loc_0041EE74: lea edx, var_24
  loc_0041EE77: mov var_2C, edx
  loc_0041EE7A: mov var_34, 00004009h
  loc_0041EE81: lea eax, var_34
  loc_0041EE84: push eax
  loc_0041EE85: call [004010F0h] ; rtcIsObject
  loc_0041EE8B: mov var_38, ax
  loc_0041EE8F: push 00406B2Ch
  loc_0041EE94: mov ecx, var_24
  loc_0041EE97: push ecx
  loc_0041EE98: call [004011D4h] ; __vbaCastObj
  loc_0041EE9E: push eax
  loc_0041EE9F: push 00423028h
  loc_0041EEA4: call [00401080h] ; __vbaObjSet
  loc_0041EEAA: mov dx, var_38
  loc_0041EEAE: mov var_40, dx
  loc_0041EEB2: lea ecx, var_24
  loc_0041EEB5: call [004011F0h] ; __vbaFreeObj
  loc_0041EEBB: movsx eax, var_40
  loc_0041EEBF: test eax, eax
  loc_0041EEC1: jz 0041EF86h
  loc_0041EEC7: mov var_4, 0000000Ah
  loc_0041EECE: lea ecx, var_3C
  loc_0041EED1: push ecx
  loc_0041EED2: mov edx, [00423028h]
  loc_0041EED8: mov eax, [edx]
  loc_0041EEDA: mov ecx, [00423028h]
  loc_0041EEE0: push ecx
  loc_0041EEE1: call [eax+00000088h]
  loc_0041EEE7: fnclex
  loc_0041EEE9: mov var_40, eax
  loc_0041EEEC: cmp var_40, 00000000h
  loc_0041EEF0: jge 0041EF12h
  loc_0041EEF2: push 00000088h
  loc_0041EEF7: push 00406924h
  loc_0041EEFC: mov edx, [00423028h]
  loc_0041EF02: push edx
  loc_0041EF03: mov eax, var_40
  loc_0041EF06: push eax
  loc_0041EF07: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041EF0D: mov var_60, eax
  loc_0041EF10: jmp 0041EF19h
  loc_0041EF12: mov var_60, 00000000h
  loc_0041EF19: cmp var_3C, 00000001h
  loc_0041EF1D: jnz 0041EF66h
  loc_0041EF1F: mov var_4, 0000000Bh
  loc_0041EF26: mov ecx, [00423028h]
  loc_0041EF2C: mov edx, [ecx]
  loc_0041EF2E: mov eax, [00423028h]
  loc_0041EF33: push eax
  loc_0041EF34: call [edx+0000003Ch]
  loc_0041EF37: fnclex
  loc_0041EF39: mov var_40, eax
  loc_0041EF3C: cmp var_40, 00000000h
  loc_0041EF40: jge 0041EF5Fh
  loc_0041EF42: push 0000003Ch
  loc_0041EF44: push 00406924h
  loc_0041EF49: mov ecx, [00423028h]
  loc_0041EF4F: push ecx
  loc_0041EF50: mov edx, var_40
  loc_0041EF53: push edx
  loc_0041EF54: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041EF5A: mov var_64, eax
  loc_0041EF5D: jmp 0041EF66h
  loc_0041EF5F: mov var_64, 00000000h
  loc_0041EF66: mov var_4, 0000000Dh
  loc_0041EF6D: push 00406B2Ch
  loc_0041EF72: push 00000000h
  loc_0041EF74: call [004011D4h] ; __vbaCastObj
  loc_0041EF7A: push eax
  loc_0041EF7B: push 00423028h
  loc_0041EF80: call [00401080h] ; __vbaObjSet
  loc_0041EF86: mov var_4, 0000000Fh
  loc_0041EF8D: call [00401034h] ; __vbaEnd
  loc_0041EF93: mov var_4, 00000011h
  loc_0041EF9A: call [00401190h] ; rtcErrObj
  loc_0041EFA0: push eax
  loc_0041EFA1: lea eax, var_24
  loc_0041EFA4: push eax
  loc_0041EFA5: call [00401080h] ; __vbaObjSet
  loc_0041EFAB: mov var_68, eax
  loc_0041EFAE: mov ecx, var_68
  loc_0041EFB1: mov edx, [ecx]
  loc_0041EFB3: mov eax, var_68
  loc_0041EFB6: push eax
  loc_0041EFB7: call [edx+00000048h]
  loc_0041EFBA: lea ecx, var_24
  loc_0041EFBD: call [004011F0h] ; __vbaFreeObj
  loc_0041EFC3: mov var_4, 00000012h
  loc_0041EFCA: push FFFFFFFFh
  loc_0041EFCC: call [0040104Ch] ; __vbaResume
  loc_0041EFD2: call [00401074h] ; __vbaExitProc
  loc_0041EFD8: push 0041EFEAh
  loc_0041EFDD: jmp 0041EFE9h
  loc_0041EFDF: lea ecx, var_24
  loc_0041EFE2: call [004011F0h] ; __vbaFreeObj
  loc_0041EFE8: ret
  loc_0041EFE9: ret
  loc_0041EFEA: mov ecx, var_20
  loc_0041EFED: mov fs:[00000000h], ecx
  loc_0041EFF4: pop edi
  loc_0041EFF5: pop esi
  loc_0041EFF6: pop ebx
  loc_0041EFF7: mov esp, ebp
  loc_0041EFF9: pop ebp
  loc_0041EFFA: ret
  loc_0041EFFB: int 03h
  loc_0041EFFC: int 03h
  loc_0041EFFD: int 03h
  loc_0041EFFE: int 03h
  loc_0041EFFF: int 03h
  loc_0041F000: push ebp
  loc_0041F001: mov ebp, esp
  loc_0041F003: sub esp, 0000000Ch
  loc_0041F006: push 00401AA6h ; __vbaExceptHandler
  loc_0041F00B: mov eax, fs:[00000000h]
  loc_0041F011: push eax
  loc_0041F012: mov fs:[00000000h], esp
  loc_0041F019: sub esp, 0000006Ch
  loc_0041F01C: push ebx
  loc_0041F01D: push esi
  loc_0041F01E: push edi
  loc_0041F01F: mov var_C, esp
  loc_0041F022: mov var_8, 00401948h
  loc_0041F029: mov eax, arg_14
  loc_0041F02C: xor edi, edi
  loc_0041F02E: mov var_18, edi
  loc_0041F031: mov var_28, edi
  loc_0041F034: cmp [eax], FFFFFFh
  loc_0041F038: mov var_2C, edi
  loc_0041F03B: mov var_30, edi
  loc_0041F03E: mov var_34, edi
  loc_0041F041: mov var_44, edi
  loc_0041F044: mov var_54, edi
  loc_0041F047: mov var_64, edi
  loc_0041F04A: mov edx, 004083BCh ; "CLOSE "
  loc_0041F04F: jz 0041F056h
  loc_0041F051: mov edx, 004083D0h ; "OPEN "
  loc_0041F056: lea ecx, var_18
  loc_0041F059: call [00401178h] ; __vbaStrCopy
  loc_0041F05F: mov ecx, arg_10
  loc_0041F062: lea edx, var_64
  loc_0041F065: push edx
  loc_0041F066: mov var_5C, ecx
  loc_0041F069: mov var_64, 00004003h
  loc_0041F070: call 0041F160h
  loc_0041F075: mov esi, [004011D0h] ; __vbaStrMove
  loc_0041F07B: mov edx, eax
  loc_0041F07D: lea ecx, var_34
  loc_0041F080: call __vbaStrMove
  loc_0041F082: mov eax, var_18
  loc_0041F085: mov edx, var_34
  loc_0041F088: push eax
  loc_0041F089: lea ecx, var_2C
  loc_0041F08C: mov var_3C, 80020004h
  loc_0041F093: mov var_44, 0000000Ah
  loc_0041F09A: mov var_34, edi
  loc_0041F09D: call __vbaStrMove
  loc_0041F09F: push eax
  loc_0041F0A0: call [00401050h] ; __vbaStrCat
  loc_0041F0A6: mov edx, eax
  loc_0041F0A8: lea ecx, var_30
  loc_0041F0AB: call __vbaStrMove
  loc_0041F0AD: mov eax, arg_C
  loc_0041F0B0: lea ecx, var_44
  loc_0041F0B3: lea edx, var_30
  loc_0041F0B6: push ecx
  loc_0041F0B7: push edx
  loc_0041F0B8: lea ecx, var_54
  loc_0041F0BB: push eax
  loc_0041F0BC: push ecx
  loc_0041F0BD: call 0041CA40h
  loc_0041F0C2: lea edx, var_34
  loc_0041F0C5: lea eax, var_30
  loc_0041F0C8: push edx
  loc_0041F0C9: lea ecx, var_2C
  loc_0041F0CC: push eax
  loc_0041F0CD: push ecx
  loc_0041F0CE: push 00000003h
  loc_0041F0D0: call [00401180h] ; __vbaFreeStrList
  loc_0041F0D6: lea edx, var_54
  loc_0041F0D9: lea eax, var_44
  loc_0041F0DC: push edx
  loc_0041F0DD: push eax
  loc_0041F0DE: push 00000002h
  loc_0041F0E0: call [00401038h] ; __vbaFreeVarList
  loc_0041F0E6: add esp, 0000001Ch
  loc_0041F0E9: push 0041F131h
  loc_0041F0EE: jmp 0041F127h
  loc_0041F0F0: test var_4, 04h
  loc_0041F0F4: jz 0041F0FFh
  loc_0041F0F6: lea ecx, var_28
  loc_0041F0F9: call [00401020h] ; __vbaFreeVar
  loc_0041F0FF: lea ecx, var_34
  loc_0041F102: lea edx, var_30
  loc_0041F105: push ecx
  loc_0041F106: lea eax, var_2C
  loc_0041F109: push edx
  loc_0041F10A: push eax
  loc_0041F10B: push 00000003h
  loc_0041F10D: call [00401180h] ; __vbaFreeStrList
  loc_0041F113: lea ecx, var_54
  loc_0041F116: lea edx, var_44
  loc_0041F119: push ecx
  loc_0041F11A: push edx
  loc_0041F11B: push 00000002h
  loc_0041F11D: call [00401038h] ; __vbaFreeVarList
  loc_0041F123: add esp, 0000001Ch
  loc_0041F126: ret
  loc_0041F127: lea ecx, var_18
  loc_0041F12A: call [004011F4h] ; __vbaFreeStr
  loc_0041F130: ret
  loc_0041F131: mov eax, arg_8
  loc_0041F134: mov edx, var_28
  loc_0041F137: mov ecx, eax
  loc_0041F139: pop edi
  loc_0041F13A: pop esi
  loc_0041F13B: pop ebx
  loc_0041F13C: mov [ecx], edx
  loc_0041F13E: mov edx, var_24
  loc_0041F141: mov [ecx+00000004h], edx
  loc_0041F144: mov edx, var_20
  loc_0041F147: mov [ecx+00000008h], edx
  loc_0041F14A: mov edx, var_1C
  loc_0041F14D: mov [ecx+0000000Ch], edx
  loc_0041F150: mov ecx, var_14
  loc_0041F153: mov fs:[00000000h], ecx
  loc_0041F15A: mov esp, ebp
  loc_0041F15C: pop ebp
  loc_0041F15D: retn 0010h
End Function

Private Function Proc_2_8_41F000(arg_C, arg_10, arg_14) '41F000
  loc_0041F000: push ebp
  loc_0041F001: mov ebp, esp
  loc_0041F003: sub esp, 0000000Ch
  loc_0041F006: push 00401AA6h ; __vbaExceptHandler
  loc_0041F00B: mov eax, fs:[00000000h]
  loc_0041F011: push eax
  loc_0041F012: mov fs:[00000000h], esp
  loc_0041F019: sub esp, 0000006Ch
  loc_0041F01C: push ebx
  loc_0041F01D: push esi
  loc_0041F01E: push edi
  loc_0041F01F: mov var_C, esp
  loc_0041F022: mov var_8, 00401948h
  loc_0041F029: mov eax, arg_14
  loc_0041F02C: xor edi, edi
  loc_0041F02E: mov var_18, edi
  loc_0041F031: mov var_28, edi
  loc_0041F034: cmp [eax], FFFFFFh
  loc_0041F038: mov var_2C, edi
  loc_0041F03B: mov var_30, edi
  loc_0041F03E: mov var_34, edi
  loc_0041F041: mov var_44, edi
  loc_0041F044: mov var_54, edi
  loc_0041F047: mov var_64, edi
  loc_0041F04A: mov edx, 004083BCh ; "CLOSE "
  loc_0041F04F: jz 0041F056h
  loc_0041F051: mov edx, 004083D0h ; "OPEN "
  loc_0041F056: lea ecx, var_18
  loc_0041F059: call [00401178h] ; __vbaStrCopy
  loc_0041F05F: mov ecx, arg_10
  loc_0041F062: lea edx, var_64
  loc_0041F065: push edx
  loc_0041F066: mov var_5C, ecx
  loc_0041F069: mov var_64, 00004003h
  loc_0041F070: call 0041F160h
  loc_0041F075: mov esi, [004011D0h] ; __vbaStrMove
  loc_0041F07B: mov edx, eax
  loc_0041F07D: lea ecx, var_34
  loc_0041F080: call __vbaStrMove
  loc_0041F082: mov eax, var_18
  loc_0041F085: mov edx, var_34
  loc_0041F088: push eax
  loc_0041F089: lea ecx, var_2C
  loc_0041F08C: mov var_3C, 80020004h
  loc_0041F093: mov var_44, 0000000Ah
  loc_0041F09A: mov var_34, edi
  loc_0041F09D: call __vbaStrMove
  loc_0041F09F: push eax
  loc_0041F0A0: call [00401050h] ; __vbaStrCat
  loc_0041F0A6: mov edx, eax
  loc_0041F0A8: lea ecx, var_30
  loc_0041F0AB: call __vbaStrMove
  loc_0041F0AD: mov eax, arg_C
  loc_0041F0B0: lea ecx, var_44
  loc_0041F0B3: lea edx, var_30
  loc_0041F0B6: push ecx
  loc_0041F0B7: push edx
  loc_0041F0B8: lea ecx, var_54
  loc_0041F0BB: push eax
  loc_0041F0BC: push ecx
  loc_0041F0BD: call 0041CA40h
  loc_0041F0C2: lea edx, var_34
  loc_0041F0C5: lea eax, var_30
  loc_0041F0C8: push edx
  loc_0041F0C9: lea ecx, var_2C
  loc_0041F0CC: push eax
  loc_0041F0CD: push ecx
  loc_0041F0CE: push 00000003h
  loc_0041F0D0: call [00401180h] ; __vbaFreeStrList
  loc_0041F0D6: lea edx, var_54
  loc_0041F0D9: lea eax, var_44
  loc_0041F0DC: push edx
  loc_0041F0DD: push eax
  loc_0041F0DE: push 00000002h
  loc_0041F0E0: call [00401038h] ; __vbaFreeVarList
  loc_0041F0E6: add esp, 0000001Ch
  loc_0041F0E9: push 0041F131h
  loc_0041F0EE: jmp 0041F127h
  loc_0041F0F0: test var_4, 04h
  loc_0041F0F4: jz 0041F0FFh
  loc_0041F0F6: lea ecx, var_28
  loc_0041F0F9: call [00401020h] ; __vbaFreeVar
  loc_0041F0FF: lea ecx, var_34
  loc_0041F102: lea edx, var_30
  loc_0041F105: push ecx
  loc_0041F106: lea eax, var_2C
  loc_0041F109: push edx
  loc_0041F10A: push eax
  loc_0041F10B: push 00000003h
  loc_0041F10D: call [00401180h] ; __vbaFreeStrList
  loc_0041F113: lea ecx, var_54
  loc_0041F116: lea edx, var_44
  loc_0041F119: push ecx
  loc_0041F11A: push edx
  loc_0041F11B: push 00000002h
  loc_0041F11D: call [00401038h] ; __vbaFreeVarList
  loc_0041F123: add esp, 0000001Ch
  loc_0041F126: ret
  loc_0041F127: lea ecx, var_18
  loc_0041F12A: call [004011F4h] ; __vbaFreeStr
  loc_0041F130: ret
  loc_0041F131: mov eax, arg_8
  loc_0041F134: mov edx, var_28
  loc_0041F137: mov ecx, eax
  loc_0041F139: pop edi
  loc_0041F13A: pop esi
  loc_0041F13B: pop ebx
  loc_0041F13C: mov [ecx], edx
  loc_0041F13E: mov edx, var_24
  loc_0041F141: mov [ecx+00000004h], edx
  loc_0041F144: mov edx, var_20
  loc_0041F147: mov [ecx+00000008h], edx
  loc_0041F14A: mov edx, var_1C
  loc_0041F14D: mov [ecx+0000000Ch], edx
  loc_0041F150: mov ecx, var_14
  loc_0041F153: mov fs:[00000000h], ecx
  loc_0041F15A: mov esp, ebp
  loc_0041F15C: pop ebp
  loc_0041F15D: retn 0010h
End Function
