
Private Sub Proc_3_0_41F160() '41F160
  loc_0041F160: push ebp
  loc_0041F161: mov ebp, esp
  loc_0041F163: sub esp, 0000000Ch
  loc_0041F166: push 00401AA6h ; __vbaExceptHandler
  loc_0041F16B: mov eax, fs:[00000000h]
  loc_0041F171: push eax
  loc_0041F172: mov fs:[00000000h], esp
  loc_0041F179: sub esp, 00000044h
  loc_0041F17C: push ebx
  loc_0041F17D: push esi
  loc_0041F17E: push edi
  loc_0041F17F: mov var_C, esp
  loc_0041F182: mov var_8, 00401958h
  loc_0041F189: mov edx, arg_8
  loc_0041F18C: xor eax, eax
  loc_0041F18E: lea ecx, var_50
  loc_0041F191: mov var_18, eax
  loc_0041F194: mov var_1C, eax
  loc_0041F197: mov var_20, eax
  loc_0041F19A: mov var_30, eax
  loc_0041F19D: mov var_40, eax
  loc_0041F1A0: mov var_50, eax
  loc_0041F1A3: call [0040101Ch] ; __vbaVarVargNofree
  loc_0041F1A9: push eax
  loc_0041F1AA: call [00401044h] ; __vbaStrErrVarCopy
  loc_0041F1B0: mov var_28, eax
  loc_0041F1B3: lea eax, var_30
  loc_0041F1B6: lea ecx, var_40
  loc_0041F1B9: push eax
  loc_0041F1BA: push ecx
  loc_0041F1BB: mov var_30, 00000008h
  loc_0041F1C2: call [004010A4h] ; rtcTrimVar
  loc_0041F1C8: lea edx, var_40
  loc_0041F1CB: push edx
  loc_0041F1CC: call [00401030h] ; __vbaStrVarMove
  loc_0041F1D2: mov esi, [004011D0h] ; __vbaStrMove
  loc_0041F1D8: mov edx, eax
  loc_0041F1DA: lea ecx, var_18
  loc_0041F1DD: call __vbaStrMove
  loc_0041F1DF: lea eax, var_40
  loc_0041F1E2: lea ecx, var_30
  loc_0041F1E5: push eax
  loc_0041F1E6: push ecx
  loc_0041F1E7: push 00000002h
  loc_0041F1E9: call [00401038h] ; __vbaFreeVarList
  loc_0041F1EF: mov edx, var_18
  loc_0041F1F2: add esp, 0000000Ch
  loc_0041F1F5: push edx
  loc_0041F1F6: call [0040102Ch] ; __vbaLenBstr
  loc_0041F1FC: cmp eax, 00000001h
  loc_0041F1FF: jnz 0041F21Bh
  loc_0041F201: mov eax, var_18
  loc_0041F204: mov edi, [00401050h] ; __vbaStrCat
  loc_0041F20A: push 004083E0h
  loc_0041F20F: push eax
  loc_0041F210: call edi
  loc_0041F212: mov edx, eax
  loc_0041F214: lea ecx, var_18
  loc_0041F217: call __vbaStrMove
  loc_0041F219: jmp 0041F221h
  loc_0041F21B: mov edi, [00401050h] ; __vbaStrCat
  loc_0041F221: mov ecx, var_18
  loc_0041F224: push 004075B0h
  loc_0041F229: push ecx
  loc_0041F22A: call edi
  loc_0041F22C: mov edx, eax
  loc_0041F22E: lea ecx, var_18
  loc_0041F231: call __vbaStrMove
  loc_0041F233: mov edx, var_18
  loc_0041F236: push 004083E8h ; "(@"
  loc_0041F23B: push edx
  loc_0041F23C: call edi
  loc_0041F23E: mov edx, eax
  loc_0041F240: lea ecx, var_20
  loc_0041F243: call __vbaStrMove
  loc_0041F245: push eax
  loc_0041F246: push 004083F4h
  loc_0041F24B: call edi
  loc_0041F24D: mov edx, eax
  loc_0041F24F: lea ecx, var_18
  loc_0041F252: call __vbaStrMove
  loc_0041F254: lea ecx, var_20
  loc_0041F257: call [004011F4h] ; __vbaFreeStr
  loc_0041F25D: mov edx, var_18
  loc_0041F260: lea ecx, var_1C
  loc_0041F263: call [00401178h] ; __vbaStrCopy
  loc_0041F269: push 0041F2A6h
  loc_0041F26E: jmp 0041F29Ch
  loc_0041F270: test var_4, 04h
  loc_0041F274: jz 0041F27Fh
  loc_0041F276: lea ecx, var_1C
  loc_0041F279: call [004011F4h] ; __vbaFreeStr
  loc_0041F27F: lea ecx, var_20
  loc_0041F282: call [004011F4h] ; __vbaFreeStr
  loc_0041F288: lea eax, var_40
  loc_0041F28B: lea ecx, var_30
  loc_0041F28E: push eax
  loc_0041F28F: push ecx
  loc_0041F290: push 00000002h
  loc_0041F292: call [00401038h] ; __vbaFreeVarList
  loc_0041F298: add esp, 0000000Ch
  loc_0041F29B: ret
  loc_0041F29C: lea ecx, var_18
  loc_0041F29F: call [004011F4h] ; __vbaFreeStr
  loc_0041F2A5: ret
  loc_0041F2A6: mov ecx, var_14
  loc_0041F2A9: mov eax, var_1C
  loc_0041F2AC: pop edi
  loc_0041F2AD: pop esi
  loc_0041F2AE: mov fs:[00000000h], ecx
  loc_0041F2B5: pop ebx
  loc_0041F2B6: mov esp, ebp
  loc_0041F2B8: pop ebp
  loc_0041F2B9: retn 0004h
End Sub

Private Sub Proc_3_1_41F2C0(arg_C) '41F2C0
  loc_0041F2C0: push ebp
  loc_0041F2C1: mov ebp, esp
  loc_0041F2C3: sub esp, 0000000Ch
  loc_0041F2C6: push 00401AA6h ; __vbaExceptHandler
  loc_0041F2CB: mov eax, fs:[00000000h]
  loc_0041F2D1: push eax
  loc_0041F2D2: mov fs:[00000000h], esp
  loc_0041F2D9: sub esp, 00000024h
  loc_0041F2DC: push ebx
  loc_0041F2DD: push esi
  loc_0041F2DE: push edi
  loc_0041F2DF: mov var_C, esp
  loc_0041F2E2: mov var_8, 00401968h
  loc_0041F2E9: mov eax, [00423054h]
  loc_0041F2EE: xor ebx, ebx
  loc_0041F2F0: cmp eax, ebx
  loc_0041F2F2: mov var_24, ebx
  loc_0041F2F5: mov var_28, ebx
  loc_0041F2F8: mov [00423030h], bx
  loc_0041F2FF: jnz 0041F316h
  loc_0041F301: push 00423054h
  loc_0041F306: push 004033BCh
  loc_0041F30B: call [00401168h] ; __vbaNew2
  loc_0041F311: mov eax, [00423054h]
  loc_0041F316: mov ecx, [eax]
  loc_0041F318: push eax
  loc_0041F319: call [ecx+00000354h]
  loc_0041F31F: mov edi, [00401080h] ; __vbaObjSet
  loc_0041F325: lea edx, var_28
  loc_0041F328: push eax
  loc_0041F329: push edx
  loc_0041F32A: call edi
  loc_0041F32C: mov ecx, arg_C
  loc_0041F32F: mov esi, eax
  loc_0041F331: mov edx, [ecx]
  loc_0041F333: mov eax, [esi]
  loc_0041F335: push edx
  loc_0041F336: push esi
  loc_0041F337: call [eax+00000064h]
  loc_0041F33A: cmp eax, ebx
  loc_0041F33C: fnclex
  loc_0041F33E: jge 0041F34Fh
  loc_0041F340: push 00000064h
  loc_0041F342: push 004056F4h
  loc_0041F347: push esi
  loc_0041F348: push eax
  loc_0041F349: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041F34F: mov ebx, [004011F0h] ; __vbaFreeObj
  loc_0041F355: lea ecx, var_28
  loc_0041F358: call ebx
  loc_0041F35A: mov eax, [00423054h]
  loc_0041F35F: test eax, eax
  loc_0041F361: jnz 0041F378h
  loc_0041F363: push 00423054h
  loc_0041F368: push 004033BCh
  loc_0041F36D: call [00401168h] ; __vbaNew2
  loc_0041F373: mov eax, [00423054h]
  loc_0041F378: mov ecx, [eax]
  loc_0041F37A: push eax
  loc_0041F37B: call [ecx+00000354h]
  loc_0041F381: lea edx, var_28
  loc_0041F384: push eax
  loc_0041F385: push edx
  loc_0041F386: call edi
  loc_0041F388: mov esi, eax
  loc_0041F38A: or edi, FFFFFFFFh
  loc_0041F38D: push edi
  loc_0041F38E: push esi
  loc_0041F38F: mov eax, [esi]
  loc_0041F391: call [eax+0000005Ch]
  loc_0041F394: test eax, eax
  loc_0041F396: fnclex
  loc_0041F398: jge 0041F3A9h
  loc_0041F39A: push 0000005Ch
  loc_0041F39C: push 004056F4h
  loc_0041F3A1: push esi
  loc_0041F3A2: push eax
  loc_0041F3A3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041F3A9: lea ecx, var_28
  loc_0041F3AC: call ebx
  loc_0041F3AE: mov esi, [004010A0h] ; rtcDoEvents
  loc_0041F3B4: call rtcDoEvents
  loc_0041F3B6: cmp [00423030h], di
  loc_0041F3BD: jnz 0041F3B4h
  loc_0041F3BF: push 0041F3E0h
  loc_0041F3C4: jmp 0041F3DFh
  loc_0041F3C6: test var_4, 04h
  loc_0041F3CA: jz 0041F3D5h
  loc_0041F3CC: lea ecx, var_24
  loc_0041F3CF: call [00401020h] ; __vbaFreeVar
  loc_0041F3D5: lea ecx, var_28
  loc_0041F3D8: call [004011F0h] ; __vbaFreeObj
  loc_0041F3DE: ret
  loc_0041F3DF: ret
  loc_0041F3E0: mov eax, arg_8
  loc_0041F3E3: mov edx, var_24
  loc_0041F3E6: mov ecx, eax
  loc_0041F3E8: pop edi
  loc_0041F3E9: pop esi
  loc_0041F3EA: pop ebx
  loc_0041F3EB: mov [ecx], edx
  loc_0041F3ED: mov edx, var_20
  loc_0041F3F0: mov [ecx+00000004h], edx
  loc_0041F3F3: mov edx, var_1C
  loc_0041F3F6: mov [ecx+00000008h], edx
  loc_0041F3F9: mov edx, var_18
  loc_0041F3FC: mov [ecx+0000000Ch], edx
  loc_0041F3FF: mov ecx, var_14
  loc_0041F402: mov fs:[00000000h], ecx
  loc_0041F409: mov esp, ebp
  loc_0041F40B: pop ebp
  loc_0041F40C: retn 0008h
End Sub

Private Function Proc_3_2_41F410(arg_C, arg_10, arg_14, arg_18, arg_1C, arg_20, arg_24, arg_28) '41F410
  loc_0041F410: push ebp
  loc_0041F411: mov ebp, esp
  loc_0041F413: sub esp, 0000000Ch
  loc_0041F416: push 00401AA6h ; __vbaExceptHandler
  loc_0041F41B: mov eax, fs:[00000000h]
  loc_0041F421: push eax
  loc_0041F422: mov fs:[00000000h], esp
  loc_0041F429: sub esp, 00000298h
  loc_0041F42F: push ebx
  loc_0041F430: push esi
  loc_0041F431: push edi
  loc_0041F432: mov var_C, esp
  loc_0041F435: mov var_8, 00401978h
  loc_0041F43C: mov ecx, arg_C
  loc_0041F43F: xor eax, eax
  loc_0041F441: mov var_1C, eax
  loc_0041F444: mov var_20, eax
  loc_0041F447: cmp [ecx], ax
  loc_0041F44A: mov var_30, eax
  loc_0041F44D: mov var_34, eax
  loc_0041F450: mov var_38, eax
  loc_0041F453: mov var_3C, eax
  loc_0041F456: mov var_4C, eax
  loc_0041F459: mov var_5C, eax
  loc_0041F45C: mov var_6C, eax
  loc_0041F45F: mov var_7C, eax
  loc_0041F462: mov var_8C, eax
  loc_0041F468: mov var_9C, eax
  loc_0041F46E: mov var_AC, eax
  loc_0041F474: mov var_BC, eax
  loc_0041F47A: mov var_CC, eax
  loc_0041F480: mov var_DC, eax
  loc_0041F486: mov var_EC, eax
  loc_0041F48C: mov var_FC, eax
  loc_0041F492: mov var_10C, eax
  loc_0041F498: mov var_11C, eax
  loc_0041F49E: mov var_12C, eax
  loc_0041F4A4: mov var_13C, eax
  loc_0041F4AA: mov var_14C, eax
  loc_0041F4B0: mov var_15C, eax
  loc_0041F4B6: mov var_16C, eax
  loc_0041F4BC: mov var_17C, eax
  loc_0041F4C2: mov var_18C, eax
  loc_0041F4C8: mov var_19C, eax
  loc_0041F4CE: mov var_1AC, eax
  loc_0041F4D4: mov var_1BC, eax
  loc_0041F4DA: mov var_1CC, eax
  loc_0041F4E0: mov var_1DC, eax
  loc_0041F4E6: mov var_1EC, eax
  loc_0041F4EC: mov var_1FC, eax
  loc_0041F4F2: mov var_20C, eax
  loc_0041F4F8: mov var_21C, eax
  loc_0041F4FE: mov var_22C, eax
  loc_0041F504: mov var_23C, eax
  loc_0041F50A: mov var_24C, eax
  loc_0041F510: mov var_25C, eax
  loc_0041F516: mov var_26C, eax
  loc_0041F51C: mov var_27C, eax
  loc_0041F522: mov var_28C, eax
  loc_0041F528: jnz 0041F91Bh
  loc_0041F52E: mov eax, [00423044h]
  loc_0041F533: mov esi, [00401050h] ; __vbaStrCat
  loc_0041F539: push 0040848Ch ; "INSERT INTO tblLampElectricalMeasurements ("
  loc_0041F53E: push 0040856Ch ; "fldTestSerial, fldDieID, fldSwitch, fldIteration, fldSetVoltage, fldVoltage, fldCurrent) "
  loc_0041F543: mov edx, [eax+0000001Ch]
  loc_0041F546: add edx, 00000001h
  loc_0041F549: jo 0041FE1Ah
  loc_0041F54F: mov [eax+0000001Ch], edx
  loc_0041F552: call __vbaStrCat
  loc_0041F554: mov edx, eax
  loc_0041F556: lea ecx, var_34
  loc_0041F559: call [004011D0h] ; __vbaStrMove
  loc_0041F55F: push eax
  loc_0041F560: push 00408624h ; "VALUES ("
  loc_0041F565: call __vbaStrCat
  loc_0041F567: mov ebx, [00401018h] ; __vbaStrI4
  loc_0041F56D: mov var_64, eax
  loc_0041F570: mov eax, arg_10
  loc_0041F573: mov esi, 00000008h
  loc_0041F578: mov var_6C, esi
  loc_0041F57B: mov ecx, [eax]
  loc_0041F57D: push ecx
  loc_0041F57E: call ebx
  loc_0041F580: mov edi, [004010A4h] ; rtcTrimVar
  loc_0041F586: mov var_44, eax
  loc_0041F589: lea edx, var_4C
  loc_0041F58C: lea eax, var_5C
  loc_0041F58F: push edx
  loc_0041F590: push eax
  loc_0041F591: mov var_4C, esi
  loc_0041F594: call edi
  loc_0041F596: mov ecx, arg_14
  loc_0041F599: mov eax, arg_18
  loc_0041F59C: mov var_204, 00408160h
  loc_0041F5A6: mov var_20C, esi
  loc_0041F5AC: mov edx, [ecx]
  loc_0041F5AE: mov ecx, [eax]
  loc_0041F5B0: push ecx
  loc_0041F5B1: mov var_214, 0040758Ch ; "'"
  loc_0041F5BB: mov var_21C, esi
  loc_0041F5C1: mov var_224, edx
  loc_0041F5C7: mov var_22C, esi
  loc_0041F5CD: mov var_234, 0040863Ch ; "',"
  loc_0041F5D7: mov var_23C, esi
  loc_0041F5DD: call ebx
  loc_0041F5DF: mov var_C4, eax
  loc_0041F5E5: lea edx, var_CC
  loc_0041F5EB: lea eax, var_DC
  loc_0041F5F1: push edx
  loc_0041F5F2: push eax
  loc_0041F5F3: mov var_CC, esi
  loc_0041F5F9: call edi
  loc_0041F5FB: mov ecx, arg_1C
  loc_0041F5FE: mov var_244, 00408160h
  loc_0041F608: mov var_24C, esi
  loc_0041F60E: mov edx, [ecx]
  loc_0041F610: push edx
  loc_0041F611: call ebx
  loc_0041F613: mov var_104, eax
  loc_0041F619: lea eax, var_10C
  loc_0041F61F: lea ecx, var_11C
  loc_0041F625: push eax
  loc_0041F626: push ecx
  loc_0041F627: mov var_10C, esi
  loc_0041F62D: call edi
  loc_0041F62F: mov eax, arg_20
  loc_0041F632: mov ebx, [00401104h] ; __vbaStrR8
  loc_0041F638: mov var_254, 00408160h
  loc_0041F642: mov var_25C, esi
  loc_0041F648: mov edx, [eax+00000004h]
  loc_0041F64B: mov eax, [eax]
  loc_0041F64D: push edx
  loc_0041F64E: push eax
  loc_0041F64F: call ebx
  loc_0041F651: lea ecx, var_14C
  loc_0041F657: lea edx, var_15C
  loc_0041F65D: push ecx
  loc_0041F65E: push edx
  loc_0041F65F: mov var_144, eax
  loc_0041F665: mov var_14C, esi
  loc_0041F66B: call edi
  loc_0041F66D: mov eax, arg_24
  loc_0041F670: mov var_264, 00408160h
  loc_0041F67A: mov var_26C, esi
  loc_0041F680: mov ecx, [eax+00000004h]
  loc_0041F683: mov edx, [eax]
  loc_0041F685: push ecx
  loc_0041F686: push edx
  loc_0041F687: call ebx
  loc_0041F689: mov var_184, eax
  loc_0041F68F: lea eax, var_18C
  loc_0041F695: lea ecx, var_19C
  loc_0041F69B: push eax
  loc_0041F69C: push ecx
  loc_0041F69D: mov var_18C, esi
  loc_0041F6A3: call edi
  loc_0041F6A5: mov eax, arg_28
  loc_0041F6A8: mov var_274, 00408160h
  loc_0041F6B2: mov var_27C, esi
  loc_0041F6B8: mov edx, [eax+00000004h]
  loc_0041F6BB: mov eax, [eax]
  loc_0041F6BD: push edx
  loc_0041F6BE: push eax
  loc_0041F6BF: call ebx
  loc_0041F6C1: lea ecx, var_1CC
  loc_0041F6C7: lea edx, var_1DC
  loc_0041F6CD: push ecx
  loc_0041F6CE: push edx
  loc_0041F6CF: mov var_1C4, eax
  loc_0041F6D5: mov var_1CC, esi
  loc_0041F6DB: call edi
  loc_0041F6DD: mov eax, [00423044h]
  loc_0041F6E2: mov var_284, 004083F4h
  loc_0041F6EC: mov var_28C, esi
  loc_0041F6F2: mov eax, [eax+0000001Ch]
  loc_0041F6F5: cmp eax, 0000003Dh
  loc_0041F6F8: mov var_290, eax
  loc_0041F6FE: jb 0041F706h
  loc_0041F700: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041F706: mov ebx, [004011ACh] ; __vbaVarAdd
  loc_0041F70C: lea ecx, var_6C
  loc_0041F70F: lea edx, var_5C
  loc_0041F712: push ecx
  loc_0041F713: lea eax, var_7C
  loc_0041F716: push edx
  loc_0041F717: push eax
  loc_0041F718: call ebx
  loc_0041F71A: lea ecx, var_20C
  loc_0041F720: push eax
  loc_0041F721: lea edx, var_8C
  loc_0041F727: push ecx
  loc_0041F728: push edx
  loc_0041F729: call ebx
  loc_0041F72B: push eax
  loc_0041F72C: lea eax, var_21C
  loc_0041F732: lea ecx, var_9C
  loc_0041F738: push eax
  loc_0041F739: push ecx
  loc_0041F73A: call ebx
  loc_0041F73C: push eax
  loc_0041F73D: lea edx, var_22C
  loc_0041F743: lea eax, var_AC
  loc_0041F749: push edx
  loc_0041F74A: push eax
  loc_0041F74B: call ebx
  loc_0041F74D: lea ecx, var_23C
  loc_0041F753: push eax
  loc_0041F754: lea edx, var_BC
  loc_0041F75A: push ecx
  loc_0041F75B: push edx
  loc_0041F75C: call ebx
  loc_0041F75E: push eax
  loc_0041F75F: lea eax, var_DC
  loc_0041F765: lea ecx, var_EC
  loc_0041F76B: push eax
  loc_0041F76C: push ecx
  loc_0041F76D: call ebx
  loc_0041F76F: push eax
  loc_0041F770: lea edx, var_24C
  loc_0041F776: lea eax, var_FC
  loc_0041F77C: push edx
  loc_0041F77D: push eax
  loc_0041F77E: call ebx
  loc_0041F780: lea ecx, var_11C
  loc_0041F786: push eax
  loc_0041F787: lea edx, var_12C
  loc_0041F78D: push ecx
  loc_0041F78E: push edx
  loc_0041F78F: call ebx
  loc_0041F791: push eax
  loc_0041F792: lea eax, var_25C
  loc_0041F798: lea ecx, var_13C
  loc_0041F79E: push eax
  loc_0041F79F: push ecx
  loc_0041F7A0: call ebx
  loc_0041F7A2: push eax
  loc_0041F7A3: lea edx, var_15C
  loc_0041F7A9: lea eax, var_16C
  loc_0041F7AF: push edx
  loc_0041F7B0: push eax
  loc_0041F7B1: call ebx
  loc_0041F7B3: lea ecx, var_26C
  loc_0041F7B9: push eax
  loc_0041F7BA: lea edx, var_17C
  loc_0041F7C0: push ecx
  loc_0041F7C1: push edx
  loc_0041F7C2: call ebx
  loc_0041F7C4: push eax
  loc_0041F7C5: lea eax, var_19C
  loc_0041F7CB: lea ecx, var_1AC
  loc_0041F7D1: push eax
  loc_0041F7D2: push ecx
  loc_0041F7D3: call ebx
  loc_0041F7D5: push eax
  loc_0041F7D6: lea edx, var_27C
  loc_0041F7DC: lea eax, var_1BC
  loc_0041F7E2: push edx
  loc_0041F7E3: push eax
  loc_0041F7E4: call ebx
  loc_0041F7E6: push eax
  loc_0041F7E7: lea ecx, var_1DC
  loc_0041F7ED: lea edx, var_1EC
  loc_0041F7F3: push ecx
  loc_0041F7F4: push edx
  loc_0041F7F5: call ebx
  loc_0041F7F7: push eax
  loc_0041F7F8: lea eax, var_28C
  loc_0041F7FE: lea ecx, var_1FC
  loc_0041F804: push eax
  loc_0041F805: push ecx
  loc_0041F806: call ebx
  loc_0041F808: push eax
  loc_0041F809: call [00401030h] ; __vbaStrVarMove
  loc_0041F80F: mov edx, eax
  loc_0041F811: lea ecx, var_38
  loc_0041F814: call [004011D0h] ; __vbaStrMove
  loc_0041F81A: mov edx, eax
  loc_0041F81C: mov eax, [00423044h]
  loc_0041F821: mov ecx, [eax+00000010h]
  loc_0041F824: mov eax, var_290
  loc_0041F82A: lea ecx, [ecx+eax*4]
  loc_0041F82D: call [00401178h] ; __vbaStrCopy
  loc_0041F833: lea ecx, var_38
  loc_0041F836: lea edx, var_34
  loc_0041F839: push ecx
  loc_0041F83A: push edx
  loc_0041F83B: push 00000002h
  loc_0041F83D: call [00401180h] ; __vbaFreeStrList
  loc_0041F843: lea eax, var_1FC
  loc_0041F849: lea ecx, var_1EC
  loc_0041F84F: push eax
  loc_0041F850: lea edx, var_1DC
  loc_0041F856: push ecx
  loc_0041F857: lea eax, var_1BC
  loc_0041F85D: push edx
  loc_0041F85E: lea ecx, var_1CC
  loc_0041F864: push eax
  loc_0041F865: lea edx, var_1AC
  loc_0041F86B: push ecx
  loc_0041F86C: lea eax, var_19C
  loc_0041F872: push edx
  loc_0041F873: lea ecx, var_17C
  loc_0041F879: push eax
  loc_0041F87A: lea edx, var_18C
  loc_0041F880: push ecx
  loc_0041F881: lea eax, var_16C
  loc_0041F887: push edx
  loc_0041F888: lea ecx, var_15C
  loc_0041F88E: push eax
  loc_0041F88F: lea edx, var_13C
  loc_0041F895: push ecx
  loc_0041F896: lea eax, var_14C
  loc_0041F89C: push edx
  loc_0041F89D: lea ecx, var_12C
  loc_0041F8A3: push eax
  loc_0041F8A4: lea edx, var_11C
  loc_0041F8AA: push ecx
  loc_0041F8AB: lea eax, var_FC
  loc_0041F8B1: push edx
  loc_0041F8B2: lea ecx, var_10C
  loc_0041F8B8: push eax
  loc_0041F8B9: lea edx, var_EC
  loc_0041F8BF: push ecx
  loc_0041F8C0: lea eax, var_DC
  loc_0041F8C6: push edx
  loc_0041F8C7: lea ecx, var_BC
  loc_0041F8CD: push eax
  loc_0041F8CE: lea edx, var_CC
  loc_0041F8D4: push ecx
  loc_0041F8D5: lea eax, var_AC
  loc_0041F8DB: push edx
  loc_0041F8DC: lea ecx, var_9C
  loc_0041F8E2: push eax
  loc_0041F8E3: lea edx, var_8C
  loc_0041F8E9: push ecx
  loc_0041F8EA: lea eax, var_7C
  loc_0041F8ED: push edx
  loc_0041F8EE: lea ecx, var_5C
  loc_0041F8F1: push eax
  loc_0041F8F2: push ecx
  loc_0041F8F3: lea edx, var_6C
  loc_0041F8F6: lea eax, var_4C
  loc_0041F8F9: push edx
  loc_0041F8FA: push eax
  loc_0041F8FB: push 0000001Ch
  loc_0041F8FD: call [00401038h] ; __vbaFreeVarList
  loc_0041F903: mov ecx, [00423044h]
  loc_0041F909: add esp, 00000080h
  loc_0041F90F: cmp [ecx+0000001Ch], 0000003Ch
  loc_0041F913: jl 0041FCDEh
  loc_0041F919: jmp 0041F92Ch
  loc_0041F91B: mov ebx, [004011ACh] ; __vbaVarAdd
  loc_0041F921: mov edi, [004010A4h] ; rtcTrimVar
  loc_0041F927: mov esi, 00000008h
  loc_0041F92C: cmp [0042303Eh], 0000h
  loc_0041F934: jnz 0041FAAAh
  loc_0041F93A: push 00408664h
  loc_0041F93F: call [00401110h] ; __vbaNew
  loc_0041F945: lea edx, var_20
  loc_0041F948: push eax
  loc_0041F949: push edx
  loc_0041F94A: call [00401080h] ; __vbaObjSet
  loc_0041F950: sub esp, 00000010h
  loc_0041F953: mov eax, [00423028h]
  loc_0041F958: mov edx, var_20
  loc_0041F95B: mov edi, esp
  loc_0041F95D: mov ecx, 00000009h
  loc_0041F962: mov var_204, eax
  loc_0041F968: mov var_20C, ecx
  loc_0041F96E: mov esi, [edx]
  loc_0041F970: mov [edi], ecx
  loc_0041F972: mov ecx, var_208
  loc_0041F978: push edx
  loc_0041F979: mov [edi+00000004h], ecx
  loc_0041F97C: mov [edi+00000008h], eax
  loc_0041F97F: mov eax, var_200
  loc_0041F985: mov [edi+0000000Ch], eax
  loc_0041F988: call [esi+00000028h]
  loc_0041F98B: test eax, eax
  loc_0041F98D: fnclex
  loc_0041F98F: jge 0041F9A3h
  loc_0041F991: mov ecx, var_20
  loc_0041F994: push 00000028h
  loc_0041F996: push 00408674h
  loc_0041F99B: push ecx
  loc_0041F99C: push eax
  loc_0041F99D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041F9A3: mov edx, [00423044h]
  loc_0041F9A9: mov ecx, [edx+0000001Ch]
  loc_0041F9AC: call [004010ECh] ; __vbaI2I4
  loc_0041F9B2: mov ebx, [004011B0h] ; __vbaFreeVarg
  loc_0041F9B8: mov var_29C, eax
  loc_0041F9BE: mov edi, 00000001h
  loc_0041F9C3: cmp di, var_29C
  loc_0041F9CA: jg 0041FA8Dh
  loc_0041F9D0: movsx esi, di
  loc_0041F9D3: cmp esi, 0000003Dh
  loc_0041F9D6: jb 0041F9DEh
  loc_0041F9D8: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041F9DE: mov edx, [00423044h]
  loc_0041F9E4: mov eax, var_20
  loc_0041F9E7: mov edx, [edx+00000010h]
  loc_0041F9EA: mov ecx, [eax]
  loc_0041F9EC: mov edx, [edx+esi*4]
  loc_0041F9EF: push edx
  loc_0041F9F0: push eax
  loc_0041F9F1: call [ecx+00000030h]
  loc_0041F9F4: test eax, eax
  loc_0041F9F6: fnclex
  loc_0041F9F8: jge 0041FA0Ch
  loc_0041F9FA: mov ecx, var_20
  loc_0041F9FD: push 00000030h
  loc_0041F9FF: push 00408674h
  loc_0041FA04: push ecx
  loc_0041FA05: push eax
  loc_0041FA06: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041FA0C: mov ecx, 0000000Ah
  loc_0041FA11: mov eax, 80020004h
  loc_0041FA16: mov var_5C, ecx
  loc_0041FA19: mov var_4C, ecx
  loc_0041FA1C: lea ecx, var_4C
  loc_0041FA1F: mov var_54, eax
  loc_0041FA22: mov var_44, eax
  loc_0041FA25: call ebx
  loc_0041FA27: mov eax, var_20
  loc_0041FA2A: lea ecx, var_3C
  loc_0041FA2D: push ecx
  loc_0041FA2E: lea ecx, var_5C
  loc_0041FA31: mov edx, [eax]
  loc_0041FA33: push FFFFFFFFh
  loc_0041FA35: push ecx
  loc_0041FA36: lea ecx, var_4C
  loc_0041FA39: push ecx
  loc_0041FA3A: push eax
  loc_0041FA3B: call [edx+00000044h]
  loc_0041FA3E: test eax, eax
  loc_0041FA40: fnclex
  loc_0041FA42: jge 0041FA56h
  loc_0041FA44: mov edx, var_20
  loc_0041FA47: push 00000044h
  loc_0041FA49: push 00408674h
  loc_0041FA4E: push edx
  loc_0041FA4F: push eax
  loc_0041FA50: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0041FA56: lea ecx, var_3C
  loc_0041FA59: call [004011F0h] ; __vbaFreeObj
  loc_0041FA5F: lea eax, var_5C
  loc_0041FA62: lea ecx, var_4C
  loc_0041FA65: push eax
  loc_0041FA66: push ecx
  loc_0041FA67: push 00000002h
  loc_0041FA69: call [00401038h] ; __vbaFreeVarList
  loc_0041FA6F: add esp, 0000000Ch
  loc_0041FA72: call [004010A0h] ; rtcDoEvents
  loc_0041FA78: mov eax, 00000001h
  loc_0041FA7D: add ax, di
  loc_0041FA80: jo 0041FE1Ah
  loc_0041FA86: mov edi, eax
  loc_0041FA88: jmp 0041F9C3h
  loc_0041FA8D: push 00408654h
  loc_0041FA92: push 00000000h
  loc_0041FA94: call [004011D4h] ; __vbaCastObj
  loc_0041FA9A: lea edx, var_20
  loc_0041FA9D: push eax
  loc_0041FA9E: push edx
  loc_0041FA9F: call [00401080h] ; __vbaObjSet
  loc_0041FAA5: jmp 0041FCD1h
  loc_0041FAAA: lea eax, var_20C
  loc_0041FAB0: push 00000000h
  loc_0041FAB2: push eax
  loc_0041FAB3: mov var_204, 00423040h
  loc_0041FABD: mov var_20C, 00004008h
  loc_0041FAC7: call [00401150h] ; rtcDir
  loc_0041FACD: mov edx, eax
  loc_0041FACF: lea ecx, var_1C
  loc_0041FAD2: call [004011D0h] ; __vbaStrMove
  loc_0041FAD8: lea ecx, var_4C
  loc_0041FADB: mov var_44, 80020004h
  loc_0041FAE2: push ecx
  loc_0041FAE3: mov var_4C, 0000000Ah
  loc_0041FAEA: call [00401164h] ; rtcFreeFile
  loc_0041FAF0: movsx edx, ax
  loc_0041FAF3: lea ecx, var_4C
  loc_0041FAF6: mov [00423038h], edx
  loc_0041FAFC: call [00401020h] ; __vbaFreeVar
  loc_0041FB02: mov eax, var_1C
  loc_0041FB05: push eax
  loc_0041FB06: push 00000000h
  loc_0041FB08: call [004010DCh] ; __vbaStrCmp
  loc_0041FB0E: test eax, eax
  loc_0041FB10: jnz 0041FB2Ch
  loc_0041FB12: mov ecx, [00423040h]
  loc_0041FB18: push ecx
  loc_0041FB19: mov ecx, [00423038h]
  loc_0041FB1F: call [004010ECh] ; __vbaI2I4
  loc_0041FB25: push eax
  loc_0041FB26: push FFFFFFFFh
  loc_0041FB28: push 00000002h
  loc_0041FB2A: jmp 0041FB43h
  loc_0041FB2C: mov edx, [00423040h]
  loc_0041FB32: mov ecx, [00423038h]
  loc_0041FB38: push edx
  loc_0041FB39: call [004010ECh] ; __vbaI2I4
  loc_0041FB3F: push eax
  loc_0041FB40: push FFFFFFFFh
  loc_0041FB42: push esi
  loc_0041FB43: call [0040115Ch] ; __vbaFileOpen
  loc_0041FB49: mov eax, [00423044h]
  loc_0041FB4E: mov ecx, [eax+0000001Ch]
  loc_0041FB51: call [004010ECh] ; __vbaI2I4
  loc_0041FB57: mov var_2A4, eax
  loc_0041FB5D: mov eax, 00000001h
  loc_0041FB62: mov var_18, eax
  loc_0041FB65: cmp ax, var_2A4
  loc_0041FB6C: jg 0041FBBEh
  loc_0041FB6E: movsx ecx, ax
  loc_0041FB71: cmp ecx, 0000003Dh
  loc_0041FB74: jb 0041FB7Fh
  loc_0041FB76: call [004010D8h] ; __vbaGenerateBoundsError
  loc_0041FB7C: mov eax, var_18
  loc_0041FB7F: mov ecx, [00423044h]
  loc_0041FB85: movsx eax, ax
  loc_0041FB88: mov edx, [ecx+00000010h]
  loc_0041FB8B: mov ecx, [00423038h]
  loc_0041FB91: mov eax, [edx+eax*4]
  loc_0041FB94: push eax
  loc_0041FB95: call [004010ECh] ; __vbaI2I4
  loc_0041FB9B: push eax
  loc_0041FB9C: push 0040759Ch
  loc_0041FBA1: call [00401128h] ; __vbaPrintFile
  loc_0041FBA7: mov eax, 00000001h
  loc_0041FBAC: add esp, 0000000Ch
  loc_0041FBAF: add ax, var_18
  loc_0041FBB3: jo 0041FE1Ah
  loc_0041FBB9: mov var_18, eax
  loc_0041FBBC: jmp 0041FB65h
  loc_0041FBBE: mov ecx, arg_C
  loc_0041FBC1: cmp [ecx], 0000h
  loc_0041FBC5: jz 0041FCBEh
  loc_0041FBCB: lea edx, var_4C
  loc_0041FBCE: push edx
  loc_0041FBCF: call [004011E4h] ; rtcGetPresentDate
  loc_0041FBD5: lea eax, var_4C
  loc_0041FBD8: push eax
  loc_0041FBD9: call [00401044h] ; __vbaStrErrVarCopy
  loc_0041FBDF: lea ecx, var_5C
  loc_0041FBE2: lea edx, var_6C
  loc_0041FBE5: push ecx
  loc_0041FBE6: push edx
  loc_0041FBE7: mov var_54, eax
  loc_0041FBEA: mov var_5C, esi
  loc_0041FBED: call edi
  loc_0041FBEF: mov eax, arg_10
  loc_0041FBF2: mov ecx, [eax]
  loc_0041FBF4: push ecx
  loc_0041FBF5: call [00401018h] ; __vbaStrI4
  loc_0041FBFB: mov var_94, eax
  loc_0041FC01: lea edx, var_9C
  loc_0041FC07: lea eax, var_AC
  loc_0041FC0D: push edx
  loc_0041FC0E: push eax
  loc_0041FC0F: mov var_9C, esi
  loc_0041FC15: call edi
  loc_0041FC17: lea ecx, var_20C
  loc_0041FC1D: lea edx, var_6C
  loc_0041FC20: push ecx
  loc_0041FC21: lea eax, var_7C
  loc_0041FC24: push edx
  loc_0041FC25: push eax
  loc_0041FC26: mov var_204, 00408688h ; "UPDATE tblLampElectricalTest set fldEndDate = #"
  loc_0041FC30: mov var_20C, esi
  loc_0041FC36: mov var_214, 004086ECh ; "# Where fldTestSerial ="
  loc_0041FC40: mov var_21C, esi
  loc_0041FC46: call ebx
  loc_0041FC48: lea ecx, var_21C
  loc_0041FC4E: push eax
  loc_0041FC4F: lea edx, var_8C
  loc_0041FC55: push ecx
  loc_0041FC56: push edx
  loc_0041FC57: call ebx
  loc_0041FC59: push eax
  loc_0041FC5A: lea eax, var_AC
  loc_0041FC60: lea ecx, var_BC
  loc_0041FC66: push eax
  loc_0041FC67: push ecx
  loc_0041FC68: call ebx
  loc_0041FC6A: mov ecx, [00423038h]
  loc_0041FC70: push eax
  loc_0041FC71: call [004010ECh] ; __vbaI2I4
  loc_0041FC77: push eax
  loc_0041FC78: push 00407F88h
  loc_0041FC7D: call [00401128h] ; __vbaPrintFile
  loc_0041FC83: lea edx, var_BC
  loc_0041FC89: lea eax, var_AC
  loc_0041FC8F: push edx
  loc_0041FC90: lea ecx, var_8C
  loc_0041FC96: push eax
  loc_0041FC97: lea edx, var_9C
  loc_0041FC9D: push ecx
  loc_0041FC9E: lea eax, var_7C
  loc_0041FCA1: push edx
  loc_0041FCA2: lea ecx, var_6C
  loc_0041FCA5: push eax
  loc_0041FCA6: lea edx, var_5C
  loc_0041FCA9: push ecx
  loc_0041FCAA: lea eax, var_4C
  loc_0041FCAD: push edx
  loc_0041FCAE: lea ecx, var_4C
  loc_0041FCB1: push eax
  loc_0041FCB2: push ecx
  loc_0041FCB3: push 00000009h
  loc_0041FCB5: call [00401038h] ; __vbaFreeVarList
  loc_0041FCBB: add esp, 00000034h
  loc_0041FCBE: mov ecx, [00423038h]
  loc_0041FCC4: call [004010ECh] ; __vbaI2I4
  loc_0041FCCA: push eax
  loc_0041FCCB: call [004010CCh] ; __vbaFileClose
  loc_0041FCD1: mov edx, [00423044h]
  loc_0041FCD7: mov [edx+0000001Ch], 00000000h
  loc_0041FCDE: fwait
  loc_0041FCDF: push 0041FDEBh
  loc_0041FCE4: jmp 0041FDD8h
  loc_0041FCE9: test var_4, 04h
  loc_0041FCED: jz 0041FCF8h
  loc_0041FCEF: lea ecx, var_30
  loc_0041FCF2: call [00401020h] ; __vbaFreeVar
  loc_0041FCF8: lea eax, var_38
  loc_0041FCFB: lea ecx, var_34
  loc_0041FCFE: push eax
  loc_0041FCFF: push ecx
  loc_0041FD00: push 00000002h
  loc_0041FD02: call [00401180h] ; __vbaFreeStrList
  loc_0041FD08: add esp, 0000000Ch
  loc_0041FD0B: lea ecx, var_3C
  loc_0041FD0E: call [004011F0h] ; __vbaFreeObj
  loc_0041FD14: lea edx, var_1FC
  loc_0041FD1A: lea eax, var_1EC
  loc_0041FD20: push edx
  loc_0041FD21: lea ecx, var_1DC
  loc_0041FD27: push eax
  loc_0041FD28: lea edx, var_1CC
  loc_0041FD2E: push ecx
  loc_0041FD2F: lea eax, var_1BC
  loc_0041FD35: push edx
  loc_0041FD36: lea ecx, var_1AC
  loc_0041FD3C: push eax
  loc_0041FD3D: lea edx, var_19C
  loc_0041FD43: push ecx
  loc_0041FD44: lea eax, var_18C
  loc_0041FD4A: push edx
  loc_0041FD4B: lea ecx, var_17C
  loc_0041FD51: push eax
  loc_0041FD52: lea edx, var_16C
  loc_0041FD58: push ecx
  loc_0041FD59: lea eax, var_15C
  loc_0041FD5F: push edx
  loc_0041FD60: lea ecx, var_14C
  loc_0041FD66: push eax
  loc_0041FD67: lea edx, var_13C
  loc_0041FD6D: push ecx
  loc_0041FD6E: lea eax, var_12C
  loc_0041FD74: push edx
  loc_0041FD75: lea ecx, var_11C
  loc_0041FD7B: push eax
  loc_0041FD7C: lea edx, var_10C
  loc_0041FD82: push ecx
  loc_0041FD83: lea eax, var_FC
  loc_0041FD89: push edx
  loc_0041FD8A: lea ecx, var_EC
  loc_0041FD90: push eax
  loc_0041FD91: lea edx, var_DC
  loc_0041FD97: push ecx
  loc_0041FD98: lea eax, var_CC
  loc_0041FD9E: push edx
  loc_0041FD9F: lea ecx, var_BC
  loc_0041FDA5: push eax
  loc_0041FDA6: lea edx, var_AC
  loc_0041FDAC: push ecx
  loc_0041FDAD: lea eax, var_9C
  loc_0041FDB3: push edx
  loc_0041FDB4: lea ecx, var_8C
  loc_0041FDBA: push eax
  loc_0041FDBB: lea edx, var_7C
  loc_0041FDBE: push ecx
  loc_0041FDBF: lea eax, var_6C
  loc_0041FDC2: push edx
  loc_0041FDC3: lea ecx, var_5C
  loc_0041FDC6: push eax
  loc_0041FDC7: lea edx, var_4C
  loc_0041FDCA: push ecx
  loc_0041FDCB: push edx
  loc_0041FDCC: push 0000001Ch
  loc_0041FDCE: call [00401038h] ; __vbaFreeVarList
  loc_0041FDD4: add esp, 00000074h
  loc_0041FDD7: ret
  loc_0041FDD8: lea ecx, var_1C
  loc_0041FDDB: call [004011F4h] ; __vbaFreeStr
  loc_0041FDE1: lea ecx, var_20
  loc_0041FDE4: call [004011F0h] ; __vbaFreeObj
  loc_0041FDEA: ret
  loc_0041FDEB: mov eax, arg_8
  loc_0041FDEE: mov edx, var_30
  loc_0041FDF1: mov ecx, eax
  loc_0041FDF3: pop edi
  loc_0041FDF4: pop esi
  loc_0041FDF5: pop ebx
  loc_0041FDF6: mov [ecx], edx
  loc_0041FDF8: mov edx, var_2C
  loc_0041FDFB: mov [ecx+00000004h], edx
  loc_0041FDFE: mov edx, var_28
  loc_0041FE01: mov [ecx+00000008h], edx
  loc_0041FE04: mov edx, var_24
  loc_0041FE07: mov [ecx+0000000Ch], edx
  loc_0041FE0A: mov ecx, var_14
  loc_0041FE0D: mov fs:[00000000h], ecx
  loc_0041FE14: mov esp, ebp
  loc_0041FE16: pop ebp
  loc_0041FE17: retn 0024h
End Function

Private Sub Proc_3_3_41FE20() '41FE20
  loc_0041FE20: push ebp
  loc_0041FE21: mov ebp, esp
  loc_0041FE23: sub esp, 0000000Ch
  loc_0041FE26: push 00401AA6h ; __vbaExceptHandler
  loc_0041FE2B: mov eax, fs:[00000000h]
  loc_0041FE31: push eax
  loc_0041FE32: mov fs:[00000000h], esp
  loc_0041FE39: sub esp, 00000054h
  loc_0041FE3C: push ebx
  loc_0041FE3D: push esi
  loc_0041FE3E: push edi
  loc_0041FE3F: mov var_C, esp
  loc_0041FE42: mov var_8, 00401988h
  loc_0041FE49: mov edi, [00401178h] ; __vbaStrCopy
  loc_0041FE4F: xor esi, esi
  loc_0041FE51: mov edx, 00407EC0h ; "RELAY1"
  loc_0041FE56: lea ecx, var_18
  loc_0041FE59: mov var_18, esi
  loc_0041FE5C: mov var_28, esi
  loc_0041FE5F: mov var_2C, esi
  loc_0041FE62: mov var_30, esi
  loc_0041FE65: mov var_40, esi
  loc_0041FE68: mov var_50, esi
  loc_0041FE6B: call edi
  loc_0041FE6D: mov edx, 00408720h ; "*rst;*cls;*opc?"
  loc_0041FE72: lea ecx, var_30
  loc_0041FE75: mov var_38, FFFFFFFFh
  loc_0041FE7C: mov var_40, 0000000Bh
  loc_0041FE83: call edi
  loc_0041FE85: lea eax, var_40
  loc_0041FE88: lea ecx, var_30
  loc_0041FE8B: push eax
  loc_0041FE8C: lea edx, var_18
  loc_0041FE8F: push ecx
  loc_0041FE90: lea eax, var_50
  loc_0041FE93: push edx
  loc_0041FE94: push eax
  loc_0041FE95: call 0041CA40h
  loc_0041FE9A: lea ecx, var_50
  loc_0041FE9D: push ecx
  loc_0041FE9E: call [00401030h] ; __vbaStrVarMove
  loc_0041FEA4: mov edx, eax
  loc_0041FEA6: lea ecx, var_2C
  loc_0041FEA9: call [004011D0h] ; __vbaStrMove
  loc_0041FEAF: mov ebx, [004011F4h] ; __vbaFreeStr
  loc_0041FEB5: lea ecx, var_30
  loc_0041FEB8: call ebx
  loc_0041FEBA: lea edx, var_50
  loc_0041FEBD: lea eax, var_40
  loc_0041FEC0: push edx
  loc_0041FEC1: push eax
  loc_0041FEC2: push 00000002h
  loc_0041FEC4: call [00401038h] ; __vbaFreeVarList
  loc_0041FECA: add esp, 0000000Ch
  loc_0041FECD: mov edx, 004084E8h ; "SCAN:MODE NONE"
  loc_0041FED2: lea ecx, var_30
  loc_0041FED5: mov var_38, esi
  loc_0041FED8: mov var_40, 0000000Bh
  loc_0041FEDF: call edi
  loc_0041FEE1: lea ecx, var_40
  loc_0041FEE4: lea edx, var_30
  loc_0041FEE7: push ecx
  loc_0041FEE8: lea eax, var_18
  loc_0041FEEB: push edx
  loc_0041FEEC: lea ecx, var_50
  loc_0041FEEF: push eax
  loc_0041FEF0: push ecx
  loc_0041FEF1: call 0041CA40h
  loc_0041FEF6: lea ecx, var_30
  loc_0041FEF9: call ebx
  loc_0041FEFB: lea edx, var_50
  loc_0041FEFE: lea eax, var_40
  loc_0041FF01: push edx
  loc_0041FF02: push eax
  loc_0041FF03: push 00000002h
  loc_0041FF05: call [00401038h] ; __vbaFreeVarList
  loc_0041FF0B: add esp, 0000000Ch
  loc_0041FF0E: push 0041FF52h
  loc_0041FF13: jmp 0041FF41h
  loc_0041FF15: test var_4, 04h
  loc_0041FF19: jz 0041FF24h
  loc_0041FF1B: lea ecx, var_28
  loc_0041FF1E: call [00401020h] ; __vbaFreeVar
  loc_0041FF24: lea ecx, var_30
  loc_0041FF27: call [004011F4h] ; __vbaFreeStr
  loc_0041FF2D: lea ecx, var_50
  loc_0041FF30: lea edx, var_40
  loc_0041FF33: push ecx
  loc_0041FF34: push edx
  loc_0041FF35: push 00000002h
  loc_0041FF37: call [00401038h] ; __vbaFreeVarList
  loc_0041FF3D: add esp, 0000000Ch
  loc_0041FF40: ret
  loc_0041FF41: mov esi, [004011F4h] ; __vbaFreeStr
  loc_0041FF47: lea ecx, var_18
  loc_0041FF4A: call __vbaFreeStr
  loc_0041FF4C: lea ecx, var_2C
  loc_0041FF4F: call __vbaFreeStr
  loc_0041FF51: ret
  loc_0041FF52: mov eax, arg_8
  loc_0041FF55: mov edx, var_28
  loc_0041FF58: mov ecx, eax
  loc_0041FF5A: pop edi
  loc_0041FF5B: pop esi
  loc_0041FF5C: pop ebx
  loc_0041FF5D: mov [ecx], edx
  loc_0041FF5F: mov edx, var_24
  loc_0041FF62: mov [ecx+00000004h], edx
  loc_0041FF65: mov edx, var_20
  loc_0041FF68: mov [ecx+00000008h], edx
  loc_0041FF6B: mov edx, var_1C
  loc_0041FF6E: mov [ecx+0000000Ch], edx
  loc_0041FF71: mov ecx, var_14
  loc_0041FF74: mov fs:[00000000h], ecx
  loc_0041FF7B: mov esp, ebp
  loc_0041FF7D: pop ebp
  loc_0041FF7E: retn 0004h
End Sub

Private Function Proc_3_4_41FF90(arg_C, arg_10, arg_14, arg_18, arg_1C) '41FF90
  loc_0041FF90: push ebp
  loc_0041FF91: mov ebp, esp
  loc_0041FF93: sub esp, 00000008h
  loc_0041FF96: push 00401AA6h ; __vbaExceptHandler
  loc_0041FF9B: mov eax, fs:[00000000h]
  loc_0041FFA1: push eax
  loc_0041FFA2: mov fs:[00000000h], esp
  loc_0041FFA9: sub esp, 00000064h
  loc_0041FFAC: push ebx
  loc_0041FFAD: push esi
  loc_0041FFAE: push edi
  loc_0041FFAF: mov var_8, esp
  loc_0041FFB2: mov var_4, 00401998h
  loc_0041FFB9: mov esi, [00401178h] ; __vbaStrCopy
  loc_0041FFBF: xor ebx, ebx
  loc_0041FFC1: mov edx, 00407EC0h ; "RELAY1"
  loc_0041FFC6: lea ecx, var_24
  loc_0041FFC9: mov var_18, ebx
  loc_0041FFCC: mov var_1C, ebx
  loc_0041FFCF: mov var_20, ebx
  loc_0041FFD2: mov var_24, ebx
  loc_0041FFD5: mov var_28, ebx
  loc_0041FFD8: mov var_2C, ebx
  loc_0041FFDB: mov var_3C, ebx
  loc_0041FFDE: mov var_4C, ebx
  loc_0041FFE1: mov var_5C, ebx
  loc_0041FFE4: mov var_70, ebx
  loc_0041FFE7: call __vbaStrCopy
  loc_0041FFE9: mov eax, arg_8
  loc_0041FFEC: mov edx, arg_14
  loc_0041FFEF: mov ecx, [eax]
  loc_0041FFF1: sub ecx, 00000001h
  loc_0041FFF4: jo 004201ECh
  loc_0041FFFA: cmp [edx], bx
  loc_0041FFFD: mov var_20, ecx
  loc_00420000: jz 0042003Bh
  loc_00420002: lea eax, var_70
  loc_00420005: lea ecx, var_20
  loc_00420008: push eax
  loc_00420009: lea edx, var_24
  loc_0042000C: push ecx
  loc_0042000D: lea eax, var_3C
  loc_00420010: push edx
  loc_00420011: push eax
  loc_00420012: mov var_70, FFFFFFFFh
  loc_00420019: call 0041F000h
  loc_0042001E: mov edi, [00401020h] ; __vbaFreeVar
  loc_00420024: lea ecx, var_3C
  loc_00420027: call edi
  loc_00420029: mov ecx, arg_1C
  loc_0042002C: lea edx, var_3C
  loc_0042002F: push ecx
  loc_00420030: push edx
  loc_00420031: call 0041F2C0h
  loc_00420036: lea ecx, var_3C
  loc_00420039: call edi
  loc_0042003B: mov edx, 00408540h ; "READ?"
  loc_00420040: lea ecx, var_2C
  loc_00420043: mov var_34, FFFFFFFFh
  loc_0042004A: mov var_3C, 0000000Bh
  loc_00420051: call __vbaStrCopy
  loc_00420053: mov edx, 00408520h ; "Keithley2400"
  loc_00420058: lea ecx, var_28
  loc_0042005B: call __vbaStrCopy
  loc_0042005D: lea eax, var_3C
  loc_00420060: lea ecx, var_2C
  loc_00420063: push eax
  loc_00420064: lea edx, var_28
  loc_00420067: push ecx
  loc_00420068: lea eax, var_4C
  loc_0042006B: push edx
  loc_0042006C: push eax
  loc_0042006D: call 0041CA40h
  loc_00420072: lea ecx, var_4C
  loc_00420075: push ecx
  loc_00420076: call [00401030h] ; __vbaStrVarMove
  loc_0042007C: mov edx, eax
  loc_0042007E: lea ecx, var_18
  loc_00420081: call [004011D0h] ; __vbaStrMove
  loc_00420087: lea edx, var_2C
  loc_0042008A: lea eax, var_28
  loc_0042008D: push edx
  loc_0042008E: push eax
  loc_0042008F: push 00000002h
  loc_00420091: call [00401180h] ; __vbaFreeStrList
  loc_00420097: mov edi, [00401038h] ; __vbaFreeVarList
  loc_0042009D: lea ecx, var_4C
  loc_004200A0: lea edx, var_3C
  loc_004200A3: push ecx
  loc_004200A4: push edx
  loc_004200A5: push 00000002h
  loc_004200A7: call edi
  loc_004200A9: mov eax, var_18
  loc_004200AC: add esp, 00000018h
  loc_004200AF: push 00000001h
  loc_004200B1: push eax
  loc_004200B2: push 00408160h
  loc_004200B7: push ebx
  loc_004200B8: call [0040116Ch] ; __vbaInStr
  loc_004200BE: mov ecx, eax
  loc_004200C0: call [004010ECh] ; __vbaI2I4
  loc_004200C6: mov esi, eax
  loc_004200C8: lea ecx, var_18
  loc_004200CB: mov dx, si
  loc_004200CE: mov var_54, ecx
  loc_004200D1: sub dx, 0001h
  loc_004200D5: lea ecx, var_5C
  loc_004200D8: jo 004201ECh
  loc_004200DE: movsx eax, dx
  loc_004200E1: push eax
  loc_004200E2: lea edx, var_3C
  loc_004200E5: push ecx
  loc_004200E6: push edx
  loc_004200E7: mov var_5C, 00004008h
  loc_004200EE: call [004011C4h] ; rtcLeftCharVar
  loc_004200F4: lea eax, var_3C
  loc_004200F7: push eax
  loc_004200F8: call [00401134h] ; __vbaR8ErrVar
  loc_004200FE: mov ecx, arg_C
  loc_00420101: lea edx, var_3C
  loc_00420104: lea eax, var_3C
  loc_00420107: push edx
  loc_00420108: fstp real8 ptr [ecx]
  loc_0042010A: push eax
  loc_0042010B: push 00000002h
  loc_0042010D: call edi
  loc_0042010F: add esp, 0000000Ch
  loc_00420112: add si, 0001h
  loc_00420116: lea ecx, var_18
  loc_00420119: lea edx, var_3C
  loc_0042011C: jo 004201ECh
  loc_00420122: mov var_34, 80020004h
  loc_00420129: mov var_3C, 0000000Ah
  loc_00420130: mov var_54, ecx
  loc_00420133: mov var_5C, 00004008h
  loc_0042013A: push edx
  loc_0042013B: movsx eax, si
  loc_0042013E: lea ecx, var_5C
  loc_00420141: push eax
  loc_00420142: lea edx, var_4C
  loc_00420145: push ecx
  loc_00420146: push edx
  loc_00420147: call [004010BCh] ; rtcMidCharVar
  loc_0042014D: lea eax, var_4C
  loc_00420150: push eax
  loc_00420151: call [00401134h] ; __vbaR8ErrVar
  loc_00420157: mov ecx, arg_10
  loc_0042015A: lea edx, var_4C
  loc_0042015D: lea eax, var_4C
  loc_00420160: push edx
  loc_00420161: fstp real8 ptr [ecx]
  loc_00420163: lea ecx, var_3C
  loc_00420166: push eax
  loc_00420167: push ecx
  loc_00420168: push 00000003h
  loc_0042016A: call edi
  loc_0042016C: mov edx, arg_18
  loc_0042016F: add esp, 00000010h
  loc_00420172: cmp [edx], bx
  loc_00420175: jz 00420198h
  loc_00420177: lea eax, var_70
  loc_0042017A: lea ecx, var_20
  loc_0042017D: push eax
  loc_0042017E: lea edx, var_24
  loc_00420181: push ecx
  loc_00420182: lea eax, var_3C
  loc_00420185: push edx
  loc_00420186: push eax
  loc_00420187: mov var_70, ebx
  loc_0042018A: call 0041F000h
  loc_0042018F: lea ecx, var_3C
  loc_00420192: call [00401020h] ; __vbaFreeVar
  loc_00420198: fwait
  loc_00420199: push 004201D5h
  loc_0042019E: jmp 004201C4h
  loc_004201A0: lea ecx, var_2C
  loc_004201A3: lea edx, var_28
  loc_004201A6: push ecx
  loc_004201A7: push edx
  loc_004201A8: push 00000002h
  loc_004201AA: call [00401180h] ; __vbaFreeStrList
  loc_004201B0: lea eax, var_4C
  loc_004201B3: lea ecx, var_3C
  loc_004201B6: push eax
  loc_004201B7: push ecx
  loc_004201B8: push 00000002h
  loc_004201BA: call [00401038h] ; __vbaFreeVarList
  loc_004201C0: add esp, 00000018h
  loc_004201C3: ret
  loc_004201C4: mov esi, [004011F4h] ; __vbaFreeStr
  loc_004201CA: lea ecx, var_18
  loc_004201CD: call __vbaFreeStr
  loc_004201CF: lea ecx, var_24
  loc_004201D2: call __vbaFreeStr
  loc_004201D4: ret
  loc_004201D5: mov ecx, var_10
  loc_004201D8: mov ax, var_1C
  loc_004201DC: pop edi
  loc_004201DD: pop esi
  loc_004201DE: mov fs:[00000000h], ecx
  loc_004201E5: pop ebx
  loc_004201E6: mov esp, ebp
  loc_004201E8: pop ebp
  loc_004201E9: retn 0018h
End Function

Private Sub Proc_3_5_420200(arg_C, arg_10) '420200
  loc_00420200: push ebp
  loc_00420201: mov ebp, esp
  loc_00420203: sub esp, 0000000Ch
  loc_00420206: push 00401AA6h ; __vbaExceptHandler
  loc_0042020B: mov eax, fs:[00000000h]
  loc_00420211: push eax
  loc_00420212: mov fs:[00000000h], esp
  loc_00420219: sub esp, 00000094h
  loc_0042021F: push ebx
  loc_00420220: push esi
  loc_00420221: push edi
  loc_00420222: mov var_C, esp
  loc_00420225: mov var_8, 004019A8h
  loc_0042022C: mov esi, [00401178h] ; __vbaStrCopy
  loc_00420232: xor eax, eax
  loc_00420234: mov edx, 00408744h ; "*rst"
  loc_00420239: lea ecx, var_30
  loc_0042023C: mov var_24, eax
  loc_0042023F: mov var_28, eax
  loc_00420242: mov var_2C, eax
  loc_00420245: mov var_30, eax
  loc_00420248: mov var_50, eax
  loc_0042024B: mov var_60, eax
  loc_0042024E: mov var_70, eax
  loc_00420251: mov var_80, eax
  loc_00420254: mov var_38, eax
  loc_00420257: mov var_40, 0000000Bh
  loc_0042025E: call __vbaStrCopy
  loc_00420260: mov edx, 00408520h ; "Keithley2400"
  loc_00420265: lea ecx, var_2C
  loc_00420268: call __vbaStrCopy
  loc_0042026A: lea eax, var_40
  loc_0042026D: lea ecx, var_30
  loc_00420270: push eax
  loc_00420271: lea edx, var_2C
  loc_00420274: push ecx
  loc_00420275: lea eax, var_50
  loc_00420278: push edx
  loc_00420279: push eax
  loc_0042027A: call 0041CA40h
  loc_0042027F: mov edi, [00401180h] ; __vbaFreeStrList
  loc_00420285: lea ecx, var_30
  loc_00420288: lea edx, var_2C
  loc_0042028B: push ecx
  loc_0042028C: push edx
  loc_0042028D: push 00000002h
  loc_0042028F: call edi
  loc_00420291: mov ebx, [00401038h] ; __vbaFreeVarList
  loc_00420297: lea eax, var_50
  loc_0042029A: lea ecx, var_40
  loc_0042029D: push eax
  loc_0042029E: push ecx
  loc_0042029F: push 00000002h
  loc_004202A1: call ebx
  loc_004202A3: add esp, 00000018h
  loc_004202A6: mov edx, 00408754h ; "trig:cle"
  loc_004202AB: lea ecx, var_30
  loc_004202AE: mov var_38, 00000000h
  loc_004202B5: mov var_40, 0000000Bh
  loc_004202BC: call __vbaStrCopy
  loc_004202BE: mov edx, 00408520h ; "Keithley2400"
  loc_004202C3: lea ecx, var_2C
  loc_004202C6: call __vbaStrCopy
  loc_004202C8: lea edx, var_40
  loc_004202CB: lea eax, var_30
  loc_004202CE: push edx
  loc_004202CF: lea ecx, var_2C
  loc_004202D2: push eax
  loc_004202D3: lea edx, var_50
  loc_004202D6: push ecx
  loc_004202D7: push edx
  loc_004202D8: call 0041CA40h
  loc_004202DD: lea eax, var_30
  loc_004202E0: lea ecx, var_2C
  loc_004202E3: push eax
  loc_004202E4: push ecx
  loc_004202E5: push 00000002h
  loc_004202E7: call edi
  loc_004202E9: lea edx, var_50
  loc_004202EC: lea eax, var_40
  loc_004202EF: push edx
  loc_004202F0: push eax
  loc_004202F1: push 00000002h
  loc_004202F3: call ebx
  loc_004202F5: add esp, 00000018h
  loc_004202F8: mov var_38, 00000000h
  loc_004202FF: mov var_40, 0000000Bh
  loc_00420306: mov edx, 0040876Ch ; "syst:rsen off"
  loc_0042030B: lea ecx, var_30
  loc_0042030E: call __vbaStrCopy
  loc_00420310: mov edx, 00408520h ; "Keithley2400"
  loc_00420315: lea ecx, var_2C
  loc_00420318: call __vbaStrCopy
  loc_0042031A: lea ecx, var_40
  loc_0042031D: lea edx, var_30
  loc_00420320: push ecx
  loc_00420321: lea eax, var_2C
  loc_00420324: push edx
  loc_00420325: lea ecx, var_50
  loc_00420328: push eax
  loc_00420329: push ecx
  loc_0042032A: call 0041CA40h
  loc_0042032F: lea edx, var_30
  loc_00420332: lea eax, var_2C
  loc_00420335: push edx
  loc_00420336: push eax
  loc_00420337: push 00000002h
  loc_00420339: call edi
  loc_0042033B: lea ecx, var_50
  loc_0042033E: lea edx, var_40
  loc_00420341: push ecx
  loc_00420342: push edx
  loc_00420343: push 00000002h
  loc_00420345: call ebx
  loc_00420347: add esp, 00000018h
  loc_0042034A: mov edx, 0040878Ch ; "syst:err:all?"
  loc_0042034F: lea ecx, var_30
  loc_00420352: mov var_38, FFFFFFFFh
  loc_00420359: mov var_40, 0000000Bh
  loc_00420360: call __vbaStrCopy
  loc_00420362: mov edx, 00408520h ; "Keithley2400"
  loc_00420367: lea ecx, var_2C
  loc_0042036A: call __vbaStrCopy
  loc_0042036C: lea eax, var_40
  loc_0042036F: lea ecx, var_30
  loc_00420372: push eax
  loc_00420373: lea edx, var_2C
  loc_00420376: push ecx
  loc_00420377: lea eax, var_50
  loc_0042037A: push edx
  loc_0042037B: push eax
  loc_0042037C: call 0041CA40h
  loc_00420381: lea ecx, var_50
  loc_00420384: push ecx
  loc_00420385: call [00401030h] ; __vbaStrVarMove
  loc_0042038B: mov edx, eax
  loc_0042038D: lea ecx, var_28
  loc_00420390: call [004011D0h] ; __vbaStrMove
  loc_00420396: lea edx, var_30
  loc_00420399: lea eax, var_2C
  loc_0042039C: push edx
  loc_0042039D: push eax
  loc_0042039E: push 00000002h
  loc_004203A0: call edi
  loc_004203A2: lea ecx, var_50
  loc_004203A5: lea edx, var_40
  loc_004203A8: push ecx
  loc_004203A9: push edx
  loc_004203AA: push 00000002h
  loc_004203AC: call ebx
  loc_004203AE: add esp, 00000018h
  loc_004203B1: mov edx, 00408828h ; "rout:term rear"
  loc_004203B6: lea ecx, var_30
  loc_004203B9: mov var_38, 00000000h
  loc_004203C0: mov var_40, 0000000Bh
  loc_004203C7: call __vbaStrCopy
  loc_004203C9: mov edx, 00408520h ; "Keithley2400"
  loc_004203CE: lea ecx, var_2C
  loc_004203D1: call __vbaStrCopy
  loc_004203D3: lea eax, var_40
  loc_004203D6: lea ecx, var_30
  loc_004203D9: push eax
  loc_004203DA: lea edx, var_2C
  loc_004203DD: push ecx
  loc_004203DE: lea eax, var_50
  loc_004203E1: push edx
  loc_004203E2: push eax
  loc_004203E3: call 0041CA40h
  loc_004203E8: lea ecx, var_30
  loc_004203EB: push ecx
  loc_004203EC: lea edx, var_2C
  loc_004203EF: push edx
  loc_004203F0: push 00000002h
  loc_004203F2: call edi
  loc_004203F4: lea eax, var_50
  loc_004203F7: lea ecx, var_40
  loc_004203FA: push eax
  loc_004203FB: push ecx
  loc_004203FC: push 00000002h
  loc_004203FE: call ebx
  loc_00420400: add esp, 00000018h
  loc_00420403: mov edx, 0040884Ch ; "syst:guar cabl"
  loc_00420408: lea ecx, var_30
  loc_0042040B: mov var_38, 00000000h
  loc_00420412: mov var_40, 0000000Bh
  loc_00420419: call __vbaStrCopy
  loc_0042041B: mov edx, 00408520h ; "Keithley2400"
  loc_00420420: lea ecx, var_2C
  loc_00420423: call __vbaStrCopy
  loc_00420425: lea edx, var_40
  loc_00420428: lea eax, var_30
  loc_0042042B: push edx
  loc_0042042C: lea ecx, var_2C
  loc_0042042F: push eax
  loc_00420430: lea edx, var_50
  loc_00420433: push ecx
  loc_00420434: push edx
  loc_00420435: call 0041CA40h
  loc_0042043A: lea eax, var_30
  loc_0042043D: lea ecx, var_2C
  loc_00420440: push eax
  loc_00420441: push ecx
  loc_00420442: push 00000002h
  loc_00420444: call edi
  loc_00420446: lea edx, var_50
  loc_00420449: lea eax, var_40
  loc_0042044C: push edx
  loc_0042044D: push eax
  loc_0042044E: push 00000002h
  loc_00420450: call ebx
  loc_00420452: add esp, 00000018h
  loc_00420455: mov edx, 00408870h ; "syst:azer:cach off"
  loc_0042045A: lea ecx, var_30
  loc_0042045D: mov var_38, 00000000h
  loc_00420464: mov var_40, 0000000Bh
  loc_0042046B: call __vbaStrCopy
  loc_0042046D: mov edx, 00408520h ; "Keithley2400"
  loc_00420472: lea ecx, var_2C
  loc_00420475: call __vbaStrCopy
  loc_00420477: lea ecx, var_40
  loc_0042047A: lea edx, var_30
  loc_0042047D: push ecx
  loc_0042047E: lea eax, var_2C
  loc_00420481: push edx
  loc_00420482: lea ecx, var_50
  loc_00420485: push eax
  loc_00420486: push ecx
  loc_00420487: call 0041CA40h
  loc_0042048C: lea edx, var_30
  loc_0042048F: lea eax, var_2C
  loc_00420492: push edx
  loc_00420493: push eax
  loc_00420494: push 00000002h
  loc_00420496: call edi
  loc_00420498: lea ecx, var_50
  loc_0042049B: lea edx, var_40
  loc_0042049E: push ecx
  loc_0042049F: push edx
  loc_004204A0: push 00000002h
  loc_004204A2: call ebx
  loc_004204A4: add esp, 00000018h
  loc_004204A7: mov edx, 0040889Ch ; "syst:azer on"
  loc_004204AC: lea ecx, var_30
  loc_004204AF: mov var_38, 00000000h
  loc_004204B6: mov var_40, 0000000Bh
  loc_004204BD: call __vbaStrCopy
  loc_004204BF: mov edx, 00408520h ; "Keithley2400"
  loc_004204C4: lea ecx, var_2C
  loc_004204C7: call __vbaStrCopy
  loc_004204C9: lea eax, var_40
  loc_004204CC: push eax
  loc_004204CD: lea ecx, var_30
  loc_004204D0: lea edx, var_2C
  loc_004204D3: push ecx
  loc_004204D4: lea eax, var_50
  loc_004204D7: push edx
  loc_004204D8: push eax
  loc_004204D9: call 0041CA40h
  loc_004204DE: lea ecx, var_30
  loc_004204E1: lea edx, var_2C
  loc_004204E4: push ecx
  loc_004204E5: push edx
  loc_004204E6: push 00000002h
  loc_004204E8: call edi
  loc_004204EA: lea eax, var_50
  loc_004204ED: lea ecx, var_40
  loc_004204F0: push eax
  loc_004204F1: push ecx
  loc_004204F2: push 00000002h
  loc_004204F4: call ebx
  loc_004204F6: add esp, 00000018h
  loc_004204F9: mov edx, 004088BCh ; "sour:clear:auto on"
  loc_004204FE: lea ecx, var_30
  loc_00420501: mov var_38, 00000000h
  loc_00420508: mov var_40, 0000000Bh
  loc_0042050F: call __vbaStrCopy
  loc_00420511: mov edx, 00408520h ; "Keithley2400"
  loc_00420516: lea ecx, var_2C
  loc_00420519: call __vbaStrCopy
  loc_0042051B: lea edx, var_40
  loc_0042051E: lea eax, var_30
  loc_00420521: push edx
  loc_00420522: lea ecx, var_2C
  loc_00420525: push eax
  loc_00420526: lea edx, var_50
  loc_00420529: push ecx
  loc_0042052A: push edx
  loc_0042052B: call 0041CA40h
  loc_00420530: lea eax, var_30
  loc_00420533: lea ecx, var_2C
  loc_00420536: push eax
  loc_00420537: push ecx
  loc_00420538: push 00000002h
  loc_0042053A: call edi
  loc_0042053C: lea edx, var_50
  loc_0042053F: lea eax, var_40
  loc_00420542: push edx
  loc_00420543: push eax
  loc_00420544: push 00000002h
  loc_00420546: call ebx
  loc_00420548: add esp, 00000018h
  loc_0042054B: mov edx, 004088E8h ; "form asc"
  loc_00420550: lea ecx, var_30
  loc_00420553: mov var_38, 00000000h
  loc_0042055A: mov var_40, 0000000Bh
  loc_00420561: call __vbaStrCopy
  loc_00420563: mov edx, 00408520h ; "Keithley2400"
  loc_00420568: lea ecx, var_2C
  loc_0042056B: call __vbaStrCopy
  loc_0042056D: lea ecx, var_40
  loc_00420570: lea edx, var_30
  loc_00420573: push ecx
  loc_00420574: lea eax, var_2C
  loc_00420577: push edx
  loc_00420578: lea ecx, var_50
  loc_0042057B: push eax
  loc_0042057C: push ecx
  loc_0042057D: call 0041CA40h
  loc_00420582: lea edx, var_30
  loc_00420585: lea eax, var_2C
  loc_00420588: push edx
  loc_00420589: push eax
  loc_0042058A: push 00000002h
  loc_0042058C: call edi
  loc_0042058E: lea ecx, var_50
  loc_00420591: lea edx, var_40
  loc_00420594: push ecx
  loc_00420595: push edx
  loc_00420596: push 00000002h
  loc_00420598: call ebx
  loc_0042059A: add esp, 00000018h
  loc_0042059D: mov var_38, 00000000h
  loc_004205A4: mov edx, 00408900h ; "form:elem volt,curr"
  loc_004205A9: lea ecx, var_30
  loc_004205AC: mov var_40, 0000000Bh
  loc_004205B3: call __vbaStrCopy
  loc_004205B5: mov edx, 00408520h ; "Keithley2400"
  loc_004205BA: lea ecx, var_2C
  loc_004205BD: call __vbaStrCopy
  loc_004205BF: lea eax, var_40
  loc_004205C2: lea ecx, var_30
  loc_004205C5: push eax
  loc_004205C6: lea edx, var_2C
  loc_004205C9: push ecx
  loc_004205CA: lea eax, var_50
  loc_004205CD: push edx
  loc_004205CE: push eax
  loc_004205CF: call 0041CA40h
  loc_004205D4: lea ecx, var_30
  loc_004205D7: lea edx, var_2C
  loc_004205DA: push ecx
  loc_004205DB: push edx
  loc_004205DC: push 00000002h
  loc_004205DE: call edi
  loc_004205E0: lea eax, var_50
  loc_004205E3: lea ecx, var_40
  loc_004205E6: push eax
  loc_004205E7: push ecx
  loc_004205E8: push 00000002h
  loc_004205EA: call ebx
  loc_004205EC: add esp, 00000018h
  loc_004205EF: mov edx, 0040878Ch ; "syst:err:all?"
  loc_004205F4: lea ecx, var_30
  loc_004205F7: mov var_38, FFFFFFFFh
  loc_004205FE: mov var_40, 0000000Bh
  loc_00420605: call __vbaStrCopy
  loc_00420607: mov edx, 00408520h ; "Keithley2400"
  loc_0042060C: lea ecx, var_2C
  loc_0042060F: call __vbaStrCopy
  loc_00420611: lea edx, var_40
  loc_00420614: lea eax, var_30
  loc_00420617: push edx
  loc_00420618: lea ecx, var_2C
  loc_0042061B: push eax
  loc_0042061C: lea edx, var_50
  loc_0042061F: push ecx
  loc_00420620: push edx
  loc_00420621: call 0041CA40h
  loc_00420626: lea eax, var_50
  loc_00420629: push eax
  loc_0042062A: call [00401030h] ; __vbaStrVarMove
  loc_00420630: mov edx, eax
  loc_00420632: lea ecx, var_28
  loc_00420635: call [004011D0h] ; __vbaStrMove
  loc_0042063B: lea ecx, var_30
  loc_0042063E: lea edx, var_2C
  loc_00420641: push ecx
  loc_00420642: push edx
  loc_00420643: push 00000002h
  loc_00420645: call edi
  loc_00420647: lea eax, var_50
  loc_0042064A: lea ecx, var_40
  loc_0042064D: push eax
  loc_0042064E: push ecx
  loc_0042064F: push 00000002h
  loc_00420651: call ebx
  loc_00420653: add esp, 00000018h
  loc_00420656: mov edx, 0040896Ch ; "syst:clear"
  loc_0042065B: lea ecx, var_30
  loc_0042065E: mov var_38, 00000000h
  loc_00420665: mov var_40, 0000000Bh
  loc_0042066C: call __vbaStrCopy
  loc_0042066E: mov edx, 00408520h ; "Keithley2400"
  loc_00420673: lea ecx, var_2C
  loc_00420676: call __vbaStrCopy
  loc_00420678: lea edx, var_40
  loc_0042067B: lea eax, var_30
  loc_0042067E: push edx
  loc_0042067F: lea ecx, var_2C
  loc_00420682: push eax
  loc_00420683: lea edx, var_50
  loc_00420686: push ecx
  loc_00420687: push edx
  loc_00420688: call 0041CA40h
  loc_0042068D: lea eax, var_30
  loc_00420690: lea ecx, var_2C
  loc_00420693: push eax
  loc_00420694: push ecx
  loc_00420695: push 00000002h
  loc_00420697: call edi
  loc_00420699: lea edx, var_50
  loc_0042069C: lea eax, var_40
  loc_0042069F: push edx
  loc_004206A0: push eax
  loc_004206A1: push 00000002h
  loc_004206A3: call ebx
  loc_004206A5: add esp, 00000018h
  loc_004206A8: mov edx, 00408988h ; "sour:func volt"
  loc_004206AD: lea ecx, var_30
  loc_004206B0: mov var_38, 00000000h
  loc_004206B7: mov var_40, 0000000Bh
  loc_004206BE: call __vbaStrCopy
  loc_004206C0: mov edx, 00408520h ; "Keithley2400"
  loc_004206C5: lea ecx, var_2C
  loc_004206C8: call __vbaStrCopy
  loc_004206CA: lea ecx, var_40
  loc_004206CD: lea edx, var_30
  loc_004206D0: push ecx
  loc_004206D1: lea eax, var_2C
  loc_004206D4: push edx
  loc_004206D5: lea ecx, var_50
  loc_004206D8: push eax
  loc_004206D9: push ecx
  loc_004206DA: call 0041CA40h
  loc_004206DF: lea edx, var_30
  loc_004206E2: lea eax, var_2C
  loc_004206E5: push edx
  loc_004206E6: push eax
  loc_004206E7: push 00000002h
  loc_004206E9: call edi
  loc_004206EB: lea ecx, var_50
  loc_004206EE: lea edx, var_40
  loc_004206F1: push ecx
  loc_004206F2: push edx
  loc_004206F3: push 00000002h
  loc_004206F5: call ebx
  loc_004206F7: add esp, 00000018h
  loc_004206FA: mov edx, 004089ACh ; "sense:func 'curr:dc'"
  loc_004206FF: lea ecx, var_30
  loc_00420702: mov var_38, 00000000h
  loc_00420709: mov var_40, 0000000Bh
  loc_00420710: call __vbaStrCopy
  loc_00420712: mov edx, 00408520h ; "Keithley2400"
  loc_00420717: lea ecx, var_2C
  loc_0042071A: call __vbaStrCopy
  loc_0042071C: lea eax, var_40
  loc_0042071F: lea ecx, var_30
  loc_00420722: push eax
  loc_00420723: lea edx, var_2C
  loc_00420726: push ecx
  loc_00420727: lea eax, var_50
  loc_0042072A: push edx
  loc_0042072B: push eax
  loc_0042072C: call 0041CA40h
  loc_00420731: lea ecx, var_30
  loc_00420734: lea edx, var_2C
  loc_00420737: push ecx
  loc_00420738: push edx
  loc_00420739: push 00000002h
  loc_0042073B: call edi
  loc_0042073D: lea eax, var_50
  loc_00420740: lea ecx, var_40
  loc_00420743: push eax
  loc_00420744: push ecx
  loc_00420745: push 00000002h
  loc_00420747: call ebx
  loc_00420749: add esp, 00000018h
  loc_0042074C: mov edx, 004089DCh ; "SOUR:VOLT:RANG 100"
  loc_00420751: lea ecx, var_30
  loc_00420754: mov var_38, 00000000h
  loc_0042075B: mov var_40, 0000000Bh
  loc_00420762: call __vbaStrCopy
  loc_00420764: mov edx, 00408520h ; "Keithley2400"
  loc_00420769: lea ecx, var_2C
  loc_0042076C: call __vbaStrCopy
  loc_0042076E: lea edx, var_40
  loc_00420771: lea eax, var_30
  loc_00420774: push edx
  loc_00420775: lea ecx, var_2C
  loc_00420778: push eax
  loc_00420779: lea edx, var_50
  loc_0042077C: push ecx
  loc_0042077D: push edx
  loc_0042077E: call 0041CA40h
  loc_00420783: lea eax, var_30
  loc_00420786: lea ecx, var_2C
  loc_00420789: push eax
  loc_0042078A: push ecx
  loc_0042078B: push 00000002h
  loc_0042078D: call edi
  loc_0042078F: lea edx, var_50
  loc_00420792: lea eax, var_40
  loc_00420795: push edx
  loc_00420796: push eax
  loc_00420797: push 00000002h
  loc_00420799: call ebx
  loc_0042079B: mov ecx, arg_C
  loc_0042079E: add esp, 00000018h
  loc_004207A1: mov var_38, 00000000h
  loc_004207A8: mov var_40, 0000000Bh
  loc_004207AF: mov edx, [ecx]
  loc_004207B1: push 00408A08h ; "sens:curr:prot "
  loc_004207B6: push edx
  loc_004207B7: call [00401050h] ; __vbaStrCat
  loc_004207BD: mov edx, eax
  loc_004207BF: lea ecx, var_30
  loc_004207C2: call [004011D0h] ; __vbaStrMove
  loc_004207C8: mov edx, 00408520h ; "Keithley2400"
  loc_004207CD: lea ecx, var_2C
  loc_004207D0: call __vbaStrCopy
  loc_004207D2: lea eax, var_40
  loc_004207D5: lea ecx, var_30
  loc_004207D8: push eax
  loc_004207D9: lea edx, var_2C
  loc_004207DC: push ecx
  loc_004207DD: lea eax, var_50
  loc_004207E0: push edx
  loc_004207E1: push eax
  loc_004207E2: call 0041CA40h
  loc_004207E7: lea ecx, var_30
  loc_004207EA: lea edx, var_2C
  loc_004207ED: push ecx
  loc_004207EE: push edx
  loc_004207EF: push 00000002h
  loc_004207F1: call edi
  loc_004207F3: lea eax, var_50
  loc_004207F6: lea ecx, var_40
  loc_004207F9: push eax
  loc_004207FA: push ecx
  loc_004207FB: push 00000002h
  loc_004207FD: call ebx
  loc_004207FF: mov edx, arg_10
  loc_00420802: add esp, 00000018h
  loc_00420805: mov var_38, 00000000h
  loc_0042080C: mov var_40, 0000000Bh
  loc_00420813: mov eax, [edx]
  loc_00420815: push 00408A2Ch ; "sens:curr:range "
  loc_0042081A: push eax
  loc_0042081B: call [00401050h] ; __vbaStrCat
  loc_00420821: mov edx, eax
  loc_00420823: lea ecx, var_30
  loc_00420826: call [004011D0h] ; __vbaStrMove
  loc_0042082C: mov edx, 00408520h ; "Keithley2400"
  loc_00420831: lea ecx, var_2C
  loc_00420834: call __vbaStrCopy
  loc_00420836: lea ecx, var_40
  loc_00420839: lea edx, var_30
  loc_0042083C: push ecx
  loc_0042083D: lea eax, var_2C
  loc_00420840: push edx
  loc_00420841: lea ecx, var_50
  loc_00420844: push eax
  loc_00420845: push ecx
  loc_00420846: call 0041CA40h
  loc_0042084B: lea edx, var_30
  loc_0042084E: lea eax, var_2C
  loc_00420851: push edx
  loc_00420852: push eax
  loc_00420853: push 00000002h
  loc_00420855: call edi
  loc_00420857: lea ecx, var_50
  loc_0042085A: lea edx, var_40
  loc_0042085D: push ecx
  loc_0042085E: push edx
  loc_0042085F: push 00000002h
  loc_00420861: call ebx
  loc_00420863: add esp, 00000018h
  loc_00420866: push 004208B2h
  loc_0042086B: jmp 004208A8h
  loc_0042086D: test var_4, 04h
  loc_00420871: jz 0042087Ch
  loc_00420873: lea ecx, var_24
  loc_00420876: call [00401020h] ; __vbaFreeVar
  loc_0042087C: lea eax, var_30
  loc_0042087F: lea ecx, var_2C
  loc_00420882: push eax
  loc_00420883: push ecx
  loc_00420884: push 00000002h
  loc_00420886: call [00401180h] ; __vbaFreeStrList
  loc_0042088C: lea edx, var_70
  loc_0042088F: lea eax, var_60
  loc_00420892: push edx
  loc_00420893: lea ecx, var_50
  loc_00420896: push eax
  loc_00420897: lea edx, var_40
  loc_0042089A: push ecx
  loc_0042089B: push edx
  loc_0042089C: push 00000004h
  loc_0042089E: call [00401038h] ; __vbaFreeVarList
  loc_004208A4: add esp, 00000020h
  loc_004208A7: ret
  loc_004208A8: lea ecx, var_28
  loc_004208AB: call [004011F4h] ; __vbaFreeStr
  loc_004208B1: ret
  loc_004208B2: mov eax, arg_8
  loc_004208B5: mov edx, var_24
  loc_004208B8: mov ecx, eax
  loc_004208BA: pop edi
  loc_004208BB: pop esi
  loc_004208BC: pop ebx
  loc_004208BD: mov [ecx], edx
  loc_004208BF: mov edx, var_20
  loc_004208C2: mov [ecx+00000004h], edx
  loc_004208C5: mov edx, var_1C
  loc_004208C8: mov [ecx+00000008h], edx
  loc_004208CB: mov edx, var_18
  loc_004208CE: mov [ecx+0000000Ch], edx
  loc_004208D1: mov ecx, var_14
  loc_004208D4: mov fs:[00000000h], ecx
  loc_004208DB: mov esp, ebp
  loc_004208DD: pop ebp
  loc_004208DE: retn 000Ch
End Sub

Private Function Proc_3_6_4208F0(arg_C, arg_10, arg_14, arg_18, arg_1C, arg_20) '4208F0
  loc_004208F0: push ebp
  loc_004208F1: mov ebp, esp
  loc_004208F3: sub esp, 0000000Ch
  loc_004208F6: push 00401AA6h ; __vbaExceptHandler
  loc_004208FB: mov eax, fs:[00000000h]
  loc_00420901: push eax
  loc_00420902: mov fs:[00000000h], esp
  loc_00420909: sub esp, 00000094h
  loc_0042090F: push ebx
  loc_00420910: push esi
  loc_00420911: push edi
  loc_00420912: mov var_C, esp
  loc_00420915: mov var_8, 004019B8h
  loc_0042091C: mov esi, [00401178h] ; __vbaStrCopy
  loc_00420922: xor eax, eax
  loc_00420924: mov edx, 00408A54h ; "sour:volt:mode fix"
  loc_00420929: lea ecx, var_30
  loc_0042092C: mov var_24, eax
  loc_0042092F: mov var_28, eax
  loc_00420932: mov var_2C, eax
  loc_00420935: mov var_30, eax
  loc_00420938: mov var_50, eax
  loc_0042093B: mov var_60, eax
  loc_0042093E: mov var_70, eax
  loc_00420941: mov var_80, eax
  loc_00420944: mov var_90, eax
  loc_0042094A: mov var_38, eax
  loc_0042094D: mov var_40, 0000000Bh
  loc_00420954: call __vbaStrCopy
  loc_00420956: mov edx, 00408520h ; "Keithley2400"
  loc_0042095B: lea ecx, var_2C
  loc_0042095E: call __vbaStrCopy
  loc_00420960: lea eax, var_40
  loc_00420963: lea ecx, var_30
  loc_00420966: push eax
  loc_00420967: lea edx, var_2C
  loc_0042096A: push ecx
  loc_0042096B: lea eax, var_50
  loc_0042096E: push edx
  loc_0042096F: push eax
  loc_00420970: call 0041CA40h
  loc_00420975: mov edi, [00401180h] ; __vbaFreeStrList
  loc_0042097B: lea ecx, var_30
  loc_0042097E: lea edx, var_2C
  loc_00420981: push ecx
  loc_00420982: push edx
  loc_00420983: push 00000002h
  loc_00420985: call edi
  loc_00420987: mov ebx, [00401038h] ; __vbaFreeVarList
  loc_0042098D: lea eax, var_50
  loc_00420990: lea ecx, var_40
  loc_00420993: push eax
  loc_00420994: push ecx
  loc_00420995: push 00000002h
  loc_00420997: call ebx
  loc_00420999: mov eax, arg_14
  loc_0042099C: add esp, 00000018h
  loc_0042099F: mov edx, [eax+00000004h]
  loc_004209A2: mov eax, [eax]
  loc_004209A4: push edx
  loc_004209A5: push eax
  loc_004209A6: call [00401104h] ; __vbaStrR8
  loc_004209AC: lea ecx, var_40
  loc_004209AF: lea edx, var_50
  loc_004209B2: push ecx
  loc_004209B3: push edx
  loc_004209B4: mov var_38, eax
  loc_004209B7: mov var_40, 00000008h
  loc_004209BE: call [004010A4h] ; rtcTrimVar
  loc_004209C4: lea eax, var_90
  loc_004209CA: lea ecx, var_50
  loc_004209CD: push eax
  loc_004209CE: lea edx, var_60
  loc_004209D1: push ecx
  loc_004209D2: push edx
  loc_004209D3: mov var_68, 00000000h
  loc_004209DA: mov var_70, 0000000Bh
  loc_004209E1: mov var_88, 00408A80h ; "sour:del "
  loc_004209EB: mov var_90, 00000008h
  loc_004209F5: call [004011ACh] ; __vbaVarAdd
  loc_004209FB: push eax
  loc_004209FC: call [00401030h] ; __vbaStrVarMove
  loc_00420A02: mov edx, eax
  loc_00420A04: lea ecx, var_30
  loc_00420A07: call [004011D0h] ; __vbaStrMove
  loc_00420A0D: mov edx, 00408520h ; "Keithley2400"
  loc_00420A12: lea ecx, var_2C
  loc_00420A15: call __vbaStrCopy
  loc_00420A17: lea eax, var_70
  loc_00420A1A: lea ecx, var_30
  loc_00420A1D: push eax
  loc_00420A1E: lea edx, var_2C
  loc_00420A21: push ecx
  loc_00420A22: lea eax, var_80
  loc_00420A25: push edx
  loc_00420A26: push eax
  loc_00420A27: call 0041CA40h
  loc_00420A2C: lea ecx, var_30
  loc_00420A2F: lea edx, var_2C
  loc_00420A32: push ecx
  loc_00420A33: push edx
  loc_00420A34: push 00000002h
  loc_00420A36: call edi
  loc_00420A38: lea eax, var_80
  loc_00420A3B: lea ecx, var_70
  loc_00420A3E: push eax
  loc_00420A3F: lea edx, var_60
  loc_00420A42: push ecx
  loc_00420A43: lea eax, var_50
  loc_00420A46: push edx
  loc_00420A47: lea ecx, var_40
  loc_00420A4A: push eax
  loc_00420A4B: push ecx
  loc_00420A4C: push 00000005h
  loc_00420A4E: call ebx
  loc_00420A50: mov eax, arg_C
  loc_00420A53: add esp, 00000024h
  loc_00420A56: mov edx, [eax+00000004h]
  loc_00420A59: mov eax, [eax]
  loc_00420A5B: push edx
  loc_00420A5C: push eax
  loc_00420A5D: call [00401104h] ; __vbaStrR8
  loc_00420A63: lea ecx, var_40
  loc_00420A66: lea edx, var_50
  loc_00420A69: push ecx
  loc_00420A6A: push edx
  loc_00420A6B: mov var_38, eax
  loc_00420A6E: mov var_40, 00000008h
  loc_00420A75: call [004010A4h] ; rtcTrimVar
  loc_00420A7B: lea eax, var_90
  loc_00420A81: lea ecx, var_50
  loc_00420A84: push eax
  loc_00420A85: lea edx, var_60
  loc_00420A88: push ecx
  loc_00420A89: push edx
  loc_00420A8A: mov var_68, 00000000h
  loc_00420A91: mov var_70, 0000000Bh
  loc_00420A98: mov var_88, 00408A98h ; "sour:volt "
  loc_00420AA2: mov var_90, 00000008h
  loc_00420AAC: call [004011ACh] ; __vbaVarAdd
  loc_00420AB2: push eax
  loc_00420AB3: call [00401030h] ; __vbaStrVarMove
  loc_00420AB9: mov edx, eax
  loc_00420ABB: lea ecx, var_30
  loc_00420ABE: call [004011D0h] ; __vbaStrMove
  loc_00420AC4: mov edx, 00408520h ; "Keithley2400"
  loc_00420AC9: lea ecx, var_2C
  loc_00420ACC: call __vbaStrCopy
  loc_00420ACE: lea eax, var_70
  loc_00420AD1: lea ecx, var_30
  loc_00420AD4: push eax
  loc_00420AD5: lea edx, var_2C
  loc_00420AD8: push ecx
  loc_00420AD9: lea eax, var_80
  loc_00420ADC: push edx
  loc_00420ADD: push eax
  loc_00420ADE: call 0041CA40h
  loc_00420AE3: lea ecx, var_30
  loc_00420AE6: lea edx, var_2C
  loc_00420AE9: push ecx
  loc_00420AEA: push edx
  loc_00420AEB: push 00000002h
  loc_00420AED: call edi
  loc_00420AEF: lea eax, var_80
  loc_00420AF2: lea ecx, var_70
  loc_00420AF5: push eax
  loc_00420AF6: lea edx, var_60
  loc_00420AF9: push ecx
  loc_00420AFA: push edx
  loc_00420AFB: lea eax, var_50
  loc_00420AFE: lea ecx, var_40
  loc_00420B01: push eax
  loc_00420B02: push ecx
  loc_00420B03: push 00000005h
  loc_00420B05: call ebx
  loc_00420B07: mov edx, arg_18
  loc_00420B0A: add esp, 00000024h
  loc_00420B0D: mov eax, [edx]
  loc_00420B0F: push eax
  loc_00420B10: call [00401018h] ; __vbaStrI4
  loc_00420B16: lea ecx, var_40
  loc_00420B19: lea edx, var_50
  loc_00420B1C: push ecx
  loc_00420B1D: push edx
  loc_00420B1E: mov var_38, eax
  loc_00420B21: mov var_40, 00000008h
  loc_00420B28: call [004010A4h] ; rtcTrimVar
  loc_00420B2E: lea eax, var_90
  loc_00420B34: lea ecx, var_50
  loc_00420B37: push eax
  loc_00420B38: lea edx, var_60
  loc_00420B3B: push ecx
  loc_00420B3C: push edx
  loc_00420B3D: mov var_68, 00000000h
  loc_00420B44: mov var_70, 0000000Bh
  loc_00420B4B: mov var_88, 00408AC0h ; "sens:curr:nplc "
  loc_00420B55: mov var_90, 00000008h
  loc_00420B5F: call [004011ACh] ; __vbaVarAdd
  loc_00420B65: push eax
  loc_00420B66: call [00401030h] ; __vbaStrVarMove
  loc_00420B6C: mov edx, eax
  loc_00420B6E: lea ecx, var_30
  loc_00420B71: call [004011D0h] ; __vbaStrMove
  loc_00420B77: mov edx, 00408520h ; "Keithley2400"
  loc_00420B7C: lea ecx, var_2C
  loc_00420B7F: call __vbaStrCopy
  loc_00420B81: lea eax, var_70
  loc_00420B84: lea ecx, var_30
  loc_00420B87: push eax
  loc_00420B88: lea edx, var_2C
  loc_00420B8B: push ecx
  loc_00420B8C: lea eax, var_80
  loc_00420B8F: push edx
  loc_00420B90: push eax
  loc_00420B91: call 0041CA40h
  loc_00420B96: lea ecx, var_30
  loc_00420B99: lea edx, var_2C
  loc_00420B9C: push ecx
  loc_00420B9D: push edx
  loc_00420B9E: push 00000002h
  loc_00420BA0: call edi
  loc_00420BA2: lea eax, var_80
  loc_00420BA5: lea ecx, var_70
  loc_00420BA8: push eax
  loc_00420BA9: lea edx, var_60
  loc_00420BAC: push ecx
  loc_00420BAD: lea eax, var_50
  loc_00420BB0: push edx
  loc_00420BB1: lea ecx, var_40
  loc_00420BB4: push eax
  loc_00420BB5: push ecx
  loc_00420BB6: push 00000005h
  loc_00420BB8: call ebx
  loc_00420BBA: mov edx, arg_1C
  loc_00420BBD: add esp, 00000024h
  loc_00420BC0: mov var_38, 00000000h
  loc_00420BC7: mov var_40, 0000000Bh
  loc_00420BCE: mov eax, [edx]
  loc_00420BD0: push 00408A08h ; "sens:curr:prot "
  loc_00420BD5: push eax
  loc_00420BD6: call [00401050h] ; __vbaStrCat
  loc_00420BDC: mov edx, eax
  loc_00420BDE: lea ecx, var_30
  loc_00420BE1: call [004011D0h] ; __vbaStrMove
  loc_00420BE7: mov edx, 00408520h ; "Keithley2400"
  loc_00420BEC: lea ecx, var_2C
  loc_00420BEF: call __vbaStrCopy
  loc_00420BF1: lea ecx, var_40
  loc_00420BF4: lea edx, var_30
  loc_00420BF7: push ecx
  loc_00420BF8: push edx
  loc_00420BF9: lea eax, var_2C
  loc_00420BFC: lea ecx, var_50
  loc_00420BFF: push eax
  loc_00420C00: push ecx
  loc_00420C01: call 0041CA40h
  loc_00420C06: lea edx, var_30
  loc_00420C09: lea eax, var_2C
  loc_00420C0C: push edx
  loc_00420C0D: push eax
  loc_00420C0E: push 00000002h
  loc_00420C10: call edi
  loc_00420C12: lea ecx, var_50
  loc_00420C15: lea edx, var_40
  loc_00420C18: push ecx
  loc_00420C19: push edx
  loc_00420C1A: push 00000002h
  loc_00420C1C: call ebx
  loc_00420C1E: mov eax, arg_20
  loc_00420C21: add esp, 00000018h
  loc_00420C24: mov var_38, 00000000h
  loc_00420C2B: mov var_40, 0000000Bh
  loc_00420C32: mov ecx, [eax]
  loc_00420C34: push 00408A2Ch ; "sens:curr:range "
  loc_00420C39: push ecx
  loc_00420C3A: call [00401050h] ; __vbaStrCat
  loc_00420C40: mov edx, eax
  loc_00420C42: lea ecx, var_30
  loc_00420C45: call [004011D0h] ; __vbaStrMove
  loc_00420C4B: mov edx, 00408520h ; "Keithley2400"
  loc_00420C50: lea ecx, var_2C
  loc_00420C53: call __vbaStrCopy
  loc_00420C55: lea edx, var_40
  loc_00420C58: lea eax, var_30
  loc_00420C5B: push edx
  loc_00420C5C: lea ecx, var_2C
  loc_00420C5F: push eax
  loc_00420C60: lea edx, var_50
  loc_00420C63: push ecx
  loc_00420C64: push edx
  loc_00420C65: call 0041CA40h
  loc_00420C6A: lea eax, var_30
  loc_00420C6D: lea ecx, var_2C
  loc_00420C70: push eax
  loc_00420C71: push ecx
  loc_00420C72: push 00000002h
  loc_00420C74: call edi
  loc_00420C76: lea edx, var_50
  loc_00420C79: lea eax, var_40
  loc_00420C7C: push edx
  loc_00420C7D: push eax
  loc_00420C7E: push 00000002h
  loc_00420C80: call ebx
  loc_00420C82: add esp, 00000018h
  loc_00420C85: mov edx, 00408AE4h ; "sens:aver:tcon rep"
  loc_00420C8A: lea ecx, var_30
  loc_00420C8D: mov var_38, 00000000h
  loc_00420C94: mov var_40, 0000000Bh
  loc_00420C9B: call __vbaStrCopy
  loc_00420C9D: mov edx, 00408520h ; "Keithley2400"
  loc_00420CA2: lea ecx, var_2C
  loc_00420CA5: call __vbaStrCopy
  loc_00420CA7: lea ecx, var_40
  loc_00420CAA: lea edx, var_30
  loc_00420CAD: push ecx
  loc_00420CAE: lea eax, var_2C
  loc_00420CB1: push edx
  loc_00420CB2: lea ecx, var_50
  loc_00420CB5: push eax
  loc_00420CB6: push ecx
  loc_00420CB7: call 0041CA40h
  loc_00420CBC: lea edx, var_30
  loc_00420CBF: lea eax, var_2C
  loc_00420CC2: push edx
  loc_00420CC3: push eax
  loc_00420CC4: push 00000002h
  loc_00420CC6: call edi
  loc_00420CC8: lea ecx, var_50
  loc_00420CCB: lea edx, var_40
  loc_00420CCE: push ecx
  loc_00420CCF: push edx
  loc_00420CD0: push 00000002h
  loc_00420CD2: call ebx
  loc_00420CD4: mov eax, arg_10
  loc_00420CD7: add esp, 00000018h
  loc_00420CDA: mov ecx, [eax]
  loc_00420CDC: push ecx
  loc_00420CDD: call [00401018h] ; __vbaStrI4
  loc_00420CE3: mov var_38, eax
  loc_00420CE6: lea edx, var_40
  loc_00420CE9: lea eax, var_50
  loc_00420CEC: push edx
  loc_00420CED: push eax
  loc_00420CEE: mov var_40, 00000008h
  loc_00420CF5: call [004010A4h] ; rtcTrimVar
  loc_00420CFB: lea ecx, var_90
  loc_00420D01: lea edx, var_50
  loc_00420D04: push ecx
  loc_00420D05: lea eax, var_60
  loc_00420D08: push edx
  loc_00420D09: push eax
  loc_00420D0A: mov var_68, 00000000h
  loc_00420D11: mov var_70, 0000000Bh
  loc_00420D18: mov var_88, 00408B10h ; "sens:aver:coun "
  loc_00420D22: mov var_90, 00000008h
  loc_00420D2C: call [004011ACh] ; __vbaVarAdd
  loc_00420D32: push eax
  loc_00420D33: call [00401030h] ; __vbaStrVarMove
  loc_00420D39: mov edx, eax
  loc_00420D3B: lea ecx, var_30
  loc_00420D3E: call [004011D0h] ; __vbaStrMove
  loc_00420D44: mov edx, 00408520h ; "Keithley2400"
  loc_00420D49: lea ecx, var_2C
  loc_00420D4C: call __vbaStrCopy
  loc_00420D4E: lea ecx, var_70
  loc_00420D51: lea edx, var_30
  loc_00420D54: push ecx
  loc_00420D55: lea eax, var_2C
  loc_00420D58: push edx
  loc_00420D59: lea ecx, var_80
  loc_00420D5C: push eax
  loc_00420D5D: push ecx
  loc_00420D5E: call 0041CA40h
  loc_00420D63: lea edx, var_30
  loc_00420D66: lea eax, var_2C
  loc_00420D69: push edx
  loc_00420D6A: push eax
  loc_00420D6B: push 00000002h
  loc_00420D6D: call edi
  loc_00420D6F: lea ecx, var_80
  loc_00420D72: lea edx, var_70
  loc_00420D75: push ecx
  loc_00420D76: lea eax, var_60
  loc_00420D79: push edx
  loc_00420D7A: lea ecx, var_50
  loc_00420D7D: push eax
  loc_00420D7E: lea edx, var_40
  loc_00420D81: push ecx
  loc_00420D82: push edx
  loc_00420D83: push 00000005h
  loc_00420D85: call ebx
  loc_00420D87: add esp, 00000024h
  loc_00420D8A: mov edx, 00408B34h ; "sense:aver on"
  loc_00420D8F: lea ecx, var_30
  loc_00420D92: mov var_38, 00000000h
  loc_00420D99: mov var_40, 0000000Bh
  loc_00420DA0: call __vbaStrCopy
  loc_00420DA2: mov edx, 00408520h ; "Keithley2400"
  loc_00420DA7: lea ecx, var_2C
  loc_00420DAA: call __vbaStrCopy
  loc_00420DAC: lea eax, var_40
  loc_00420DAF: lea ecx, var_30
  loc_00420DB2: push eax
  loc_00420DB3: lea edx, var_2C
  loc_00420DB6: push ecx
  loc_00420DB7: lea eax, var_50
  loc_00420DBA: push edx
  loc_00420DBB: push eax
  loc_00420DBC: call 0041CA40h
  loc_00420DC1: lea ecx, var_30
  loc_00420DC4: lea edx, var_2C
  loc_00420DC7: push ecx
  loc_00420DC8: push edx
  loc_00420DC9: push 00000002h
  loc_00420DCB: call edi
  loc_00420DCD: lea eax, var_50
  loc_00420DD0: lea ecx, var_40
  loc_00420DD3: push eax
  loc_00420DD4: push ecx
  loc_00420DD5: push 00000002h
  loc_00420DD7: call ebx
  loc_00420DD9: add esp, 00000018h
  loc_00420DDC: fwait
  loc_00420DDD: push 00420E2Dh
  loc_00420DE2: jmp 00420E23h
  loc_00420DE4: test var_4, 04h
  loc_00420DE8: jz 00420DF3h
  loc_00420DEA: lea ecx, var_24
  loc_00420DED: call [00401020h] ; __vbaFreeVar
  loc_00420DF3: lea edx, var_30
  loc_00420DF6: lea eax, var_2C
  loc_00420DF9: push edx
  loc_00420DFA: push eax
  loc_00420DFB: push 00000002h
  loc_00420DFD: call [00401180h] ; __vbaFreeStrList
  loc_00420E03: lea ecx, var_80
  loc_00420E06: lea edx, var_70
  loc_00420E09: push ecx
  loc_00420E0A: lea eax, var_60
  loc_00420E0D: push edx
  loc_00420E0E: lea ecx, var_50
  loc_00420E11: push eax
  loc_00420E12: lea edx, var_40
  loc_00420E15: push ecx
  loc_00420E16: push edx
  loc_00420E17: push 00000005h
  loc_00420E19: call [00401038h] ; __vbaFreeVarList
  loc_00420E1F: add esp, 00000024h
  loc_00420E22: ret
  loc_00420E23: lea ecx, var_28
  loc_00420E26: call [004011F4h] ; __vbaFreeStr
  loc_00420E2C: ret
  loc_00420E2D: mov eax, arg_8
  loc_00420E30: mov edx, var_24
  loc_00420E33: mov ecx, eax
  loc_00420E35: pop edi
  loc_00420E36: pop esi
  loc_00420E37: pop ebx
  loc_00420E38: mov [ecx], edx
  loc_00420E3A: mov edx, var_20
  loc_00420E3D: mov [ecx+00000004h], edx
  loc_00420E40: mov edx, var_1C
  loc_00420E43: mov [ecx+00000008h], edx
  loc_00420E46: mov edx, var_18
  loc_00420E49: mov [ecx+0000000Ch], edx
  loc_00420E4C: mov ecx, var_14
  loc_00420E4F: mov fs:[00000000h], ecx
  loc_00420E56: mov esp, ebp
  loc_00420E58: pop ebp
  loc_00420E59: retn 001Ch
End Function
