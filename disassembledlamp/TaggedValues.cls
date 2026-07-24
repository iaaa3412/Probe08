VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior = 0   'vbNone
  MTSTransactionMode = 0   'NotAnMTSObject
END
Attribute VB_Name = "TaggedValues"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False


Public Property Get Count(Index As Integer) '420FD0
  loc_00420FD0: push ebp
  loc_00420FD1: mov ebp, esp
  loc_00420FD3: sub esp, 0000000Ch
  loc_00420FD6: push 00401AA6h ; __vbaExceptHandler
  loc_00420FDB: mov eax, fs:[00000000h]
  loc_00420FE1: push eax
  loc_00420FE2: mov fs:[00000000h], esp
  loc_00420FE9: sub esp, 00000014h
  loc_00420FEC: push ebx
  loc_00420FED: push esi
  loc_00420FEE: push edi
  loc_00420FEF: mov var_C, esp
  loc_00420FF2: mov var_8, 004019E8h
  loc_00420FF9: xor edi, edi
  loc_00420FFB: mov var_4, edi
  loc_00420FFE: mov esi, Me
  loc_00421001: push esi
  loc_00421002: mov eax, [esi]
  loc_00421004: call [eax+00000004h]
  loc_00421007: mov eax, [esi+00000038h]
  loc_0042100A: lea edx, var_1C
  loc_0042100D: mov var_1C, edi
  loc_00421010: push edx
  loc_00421011: mov ecx, [eax]
  loc_00421013: push eax
  loc_00421014: mov var_18, edi
  loc_00421017: call [ecx+00000024h]
  loc_0042101A: cmp eax, edi
  loc_0042101C: fnclex
  loc_0042101E: jge 00421032h
  loc_00421020: mov ecx, [esi+00000038h]
  loc_00421023: push 00000024h
  loc_00421025: push 00408BE8h
  loc_0042102A: push ecx
  loc_0042102B: push eax
  loc_0042102C: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421032: mov edx, var_1C
  loc_00421035: mov var_18, edx
  loc_00421038: mov eax, Me
  loc_0042103B: push eax
  loc_0042103C: mov ecx, [eax]
  loc_0042103E: call [ecx+00000008h]
  loc_00421041: mov edx, Index
  loc_00421044: mov eax, var_18
  loc_00421047: mov [edx], eax
  loc_00421049: mov eax, var_4
  loc_0042104C: mov ecx, var_14
  loc_0042104F: pop edi
  loc_00421050: pop esi
  loc_00421051: mov fs:[00000000h], ecx
  loc_00421058: pop ebx
  loc_00421059: mov esp, ebp
  loc_0042105B: pop ebp
  loc_0042105C: retn 0008h
End Sub

Public Property Get Separator(arg_C) '421350
  loc_00421350: push ebp
  loc_00421351: mov ebp, esp
  loc_00421353: sub esp, 0000000Ch
  loc_00421356: push 00401AA6h ; __vbaExceptHandler
  loc_0042135B: mov eax, fs:[00000000h]
  loc_00421361: push eax
  loc_00421362: mov fs:[00000000h], esp
  loc_00421369: sub esp, 0000000Ch
  loc_0042136C: push ebx
  loc_0042136D: push esi
  loc_0042136E: push edi
  loc_0042136F: mov var_C, esp
  loc_00421372: mov var_8, 00401A00h
  loc_00421379: xor edi, edi
  loc_0042137B: mov var_4, edi
  loc_0042137E: mov esi, Me
  loc_00421381: push esi
  loc_00421382: mov eax, [esi]
  loc_00421384: call [eax+00000004h]
  loc_00421387: mov ecx, arg_C
  loc_0042138A: mov var_18, edi
  loc_0042138D: mov [ecx], edi
  loc_0042138F: mov edx, [esi+00000034h]
  loc_00421392: lea ecx, var_18
  loc_00421395: call [00401178h] ; __vbaStrCopy
  loc_0042139B: push 004213ADh
  loc_004213A0: jmp 004213ACh
  loc_004213A2: lea ecx, var_18
  loc_004213A5: call [004011F4h] ; __vbaFreeStr
  loc_004213AB: ret
  loc_004213AC: ret
  loc_004213AD: mov eax, Me
  loc_004213B0: push eax
  loc_004213B1: mov edx, [eax]
  loc_004213B3: call [edx+00000008h]
  loc_004213B6: mov eax, arg_C
  loc_004213B9: mov ecx, var_18
  loc_004213BC: mov [eax], ecx
  loc_004213BE: mov eax, var_4
  loc_004213C1: mov ecx, var_14
  loc_004213C4: pop edi
  loc_004213C5: pop esi
  loc_004213C6: mov fs:[00000000h], ecx
  loc_004213CD: pop ebx
  loc_004213CE: mov esp, ebp
  loc_004213D0: pop ebp
  loc_004213D1: retn 0008h
End Sub

Public Property Let Separator(Value) '4213E0
  loc_004213E0: push ebp
  loc_004213E1: mov ebp, esp
  loc_004213E3: sub esp, 0000000Ch
  loc_004213E6: push 00401AA6h ; __vbaExceptHandler
  loc_004213EB: mov eax, fs:[00000000h]
  loc_004213F1: push eax
  loc_004213F2: mov fs:[00000000h], esp
  loc_004213F9: sub esp, 00000008h
  loc_004213FC: push ebx
  loc_004213FD: push esi
  loc_004213FE: push edi
  loc_004213FF: mov var_C, esp
  loc_00421402: mov var_8, 00401A10h
  loc_00421409: mov var_4, 00000000h
  loc_00421410: mov esi, Me
  loc_00421413: push esi
  loc_00421414: mov eax, [esi]
  loc_00421416: call [eax+00000004h]
  loc_00421419: mov ecx, Value
  loc_0042141C: mov edx, [ecx]
  loc_0042141E: lea ecx, [esi+00000034h]
  loc_00421421: call [00401178h] ; __vbaStrCopy
  loc_00421427: mov eax, Me
  loc_0042142A: push eax
  loc_0042142B: mov edx, [eax]
  loc_0042142D: call [edx+00000008h]
  loc_00421430: mov eax, var_4
  loc_00421433: mov ecx, var_14
  loc_00421436: pop edi
  loc_00421437: pop esi
  loc_00421438: mov fs:[00000000h], ecx
  loc_0042143F: pop ebx
  loc_00421440: mov esp, ebp
  loc_00421442: pop ebp
  loc_00421443: retn 0008h
End Sub

Public Property Get Exists(Tag) '421450
  loc_00421450: push ebp
  loc_00421451: mov ebp, esp
  loc_00421453: sub esp, 00000018h
  loc_00421456: push 00401AA6h ; __vbaExceptHandler
  loc_0042145B: mov eax, fs:[00000000h]
  loc_00421461: push eax
  loc_00421462: mov fs:[00000000h], esp
  loc_00421469: mov eax, 00000068h
  loc_0042146E: call 00401AA0h ; __vbaChkstk
  loc_00421473: push ebx
  loc_00421474: push esi
  loc_00421475: push edi
  loc_00421476: mov var_18, esp
  loc_00421479: mov var_14, 00401A18h ; "'"
  loc_00421480: mov var_10, 00000000h
  loc_00421487: mov var_C, 00000000h
  loc_0042148E: mov eax, Me
  loc_00421491: mov ecx, [eax]
  loc_00421493: mov edx, Me
  loc_00421496: push edx
  loc_00421497: call [ecx+00000004h]
  loc_0042149A: mov var_4, 00000001h
  loc_004214A1: mov var_4, 00000002h
  loc_004214A8: push FFFFFFFFh
  loc_004214AA: call [0040107Ch] ; __vbaOnError
  loc_004214B0: mov var_4, 00000003h
  loc_004214B7: mov eax, Tag
  loc_004214BA: mov var_54, eax
  loc_004214BD: mov var_5C, 00004008h
  loc_004214C4: lea ecx, var_3C
  loc_004214C7: push ecx
  loc_004214C8: lea edx, var_5C
  loc_004214CB: push edx
  loc_004214CC: mov eax, Me
  loc_004214CF: mov ecx, [eax+00000038h]
  loc_004214D2: mov edx, Me
  loc_004214D5: mov eax, [edx+00000038h]
  loc_004214D8: mov edx, [eax]
  loc_004214DA: push ecx
  loc_004214DB: call [edx+0000001Ch]
  loc_004214DE: fnclex
  loc_004214E0: mov var_64, eax
  loc_004214E3: cmp var_64, 00000000h
  loc_004214E7: jge 00421506h
  loc_004214E9: push 0000001Ch
  loc_004214EB: push 00408BE8h
  loc_004214F0: mov eax, Me
  loc_004214F3: mov ecx, [eax+00000038h]
  loc_004214F6: push ecx
  loc_004214F7: mov edx, var_64
  loc_004214FA: push edx
  loc_004214FB: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421501: mov var_80, eax
  loc_00421504: jmp 0042150Dh
  loc_00421506: mov var_80, 00000000h
  loc_0042150D: push 00000000h
  loc_0042150F: push 00408AB0h ; "Value"
  loc_00421514: lea eax, var_3C
  loc_00421517: push eax
  loc_00421518: lea ecx, var_4C
  loc_0042151B: push ecx
  loc_0042151C: call [004011B8h] ; __vbaVarLateMemCallLd
  loc_00421522: add esp, 00000010h
  loc_00421525: push eax
  loc_00421526: call [00401030h] ; __vbaStrVarMove
  loc_0042152C: mov edx, eax
  loc_0042152E: lea ecx, var_28
  loc_00421531: call [004011D0h] ; __vbaStrMove
  loc_00421537: lea edx, var_4C
  loc_0042153A: push edx
  loc_0042153B: lea eax, var_3C
  loc_0042153E: push eax
  loc_0042153F: push 00000002h
  loc_00421541: call [00401038h] ; __vbaFreeVarList
  loc_00421547: add esp, 0000000Ch
  loc_0042154A: mov var_4, 00000004h
  loc_00421551: call [00401190h] ; rtcErrObj
  loc_00421557: push eax
  loc_00421558: lea ecx, var_2C
  loc_0042155B: push ecx
  loc_0042155C: call [00401080h] ; __vbaObjSet
  loc_00421562: mov var_64, eax
  loc_00421565: lea edx, var_60
  loc_00421568: push edx
  loc_00421569: mov eax, var_64
  loc_0042156C: mov ecx, [eax]
  loc_0042156E: mov edx, var_64
  loc_00421571: push edx
  loc_00421572: call [ecx+0000001Ch]
  loc_00421575: fnclex
  loc_00421577: mov var_68, eax
  loc_0042157A: cmp var_68, 00000000h
  loc_0042157E: jge 0042159Dh
  loc_00421580: push 0000001Ch
  loc_00421582: push 00406F64h
  loc_00421587: mov eax, var_64
  loc_0042158A: push eax
  loc_0042158B: mov ecx, var_68
  loc_0042158E: push ecx
  loc_0042158F: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421595: mov var_84, eax
  loc_0042159B: jmp 004215A7h
  loc_0042159D: mov var_84, 00000000h
  loc_004215A7: xor edx, edx
  loc_004215A9: cmp var_60, 00000000h
  loc_004215AD: setz dl
  loc_004215B0: neg edx
  loc_004215B2: mov var_24, dx
  loc_004215B6: lea ecx, var_2C
  loc_004215B9: call [004011F0h] ; __vbaFreeObj
  loc_004215BF: mov var_4, 00000005h
  loc_004215C6: call [00401190h] ; rtcErrObj
  loc_004215CC: push eax
  loc_004215CD: lea eax, var_2C
  loc_004215D0: push eax
  loc_004215D1: call [00401080h] ; __vbaObjSet
  loc_004215D7: mov var_88, eax
  loc_004215DD: mov ecx, var_88
  loc_004215E3: mov edx, [ecx]
  loc_004215E5: mov eax, var_88
  loc_004215EB: push eax
  loc_004215EC: call [edx+00000048h]
  loc_004215EF: lea ecx, var_2C
  loc_004215F2: call [004011F0h] ; __vbaFreeObj
  loc_004215F8: push 00421626h
  loc_004215FD: jmp 0042161Ch
  loc_004215FF: lea ecx, var_2C
  loc_00421602: call [004011F0h] ; __vbaFreeObj
  loc_00421608: lea ecx, var_4C
  loc_0042160B: push ecx
  loc_0042160C: lea edx, var_3C
  loc_0042160F: push edx
  loc_00421610: push 00000002h
  loc_00421612: call [00401038h] ; __vbaFreeVarList
  loc_00421618: add esp, 0000000Ch
  loc_0042161B: ret
  loc_0042161C: lea ecx, var_28
  loc_0042161F: call [004011F4h] ; __vbaFreeStr
  loc_00421625: ret
  loc_00421626: mov eax, Me
  loc_00421629: mov ecx, [eax]
  loc_0042162B: mov edx, Me
  loc_0042162E: push edx
  loc_0042162F: call [ecx+00000008h]
  loc_00421632: mov eax, arg_10
  loc_00421635: mov cx, var_24
  loc_00421639: mov [eax], cx
  loc_0042163C: mov eax, var_10
  loc_0042163F: mov ecx, var_20
  loc_00421642: mov fs:[00000000h], ecx
  loc_00421649: pop edi
  loc_0042164A: pop esi
  loc_0042164B: pop ebx
  loc_0042164C: mov esp, ebp
  loc_0042164E: pop ebp
  loc_0042164F: retn 000Ch
End Sub

Public Function Item(Tag) '421660
  loc_00421660: push ebp
  loc_00421661: mov ebp, esp
  loc_00421663: sub esp, 0000000Ch
  loc_00421666: push 00401AA6h ; __vbaExceptHandler
  loc_0042166B: mov eax, fs:[00000000h]
  loc_00421671: push eax
  loc_00421672: mov fs:[00000000h], esp
  loc_00421679: sub esp, 00000044h
  loc_0042167C: push ebx
  loc_0042167D: push esi
  loc_0042167E: push edi
  loc_0042167F: mov var_C, esp
  loc_00421682: mov var_8, 00401A50h
  loc_00421689: xor edi, edi
  loc_0042168B: mov var_4, edi
  loc_0042168E: mov esi, Me
  loc_00421691: push esi
  loc_00421692: mov eax, [esi]
  loc_00421694: call [eax+00000004h]
  loc_00421697: mov ecx, arg_10
  loc_0042169A: mov ebx, Tag
  loc_0042169D: lea eax, var_4C
  loc_004216A0: mov var_18, edi
  loc_004216A3: mov [ecx], edi
  loc_004216A5: mov edx, [esi]
  loc_004216A7: push eax
  loc_004216A8: push ebx
  loc_004216A9: push esi
  loc_004216AA: mov var_28, edi
  loc_004216AD: mov var_38, edi
  loc_004216B0: mov var_48, edi
  loc_004216B3: mov var_4C, edi
  loc_004216B6: call [edx+00000028h]
  loc_004216B9: cmp eax, edi
  loc_004216BB: jge 004216CCh
  loc_004216BD: push 00000028h
  loc_004216BF: push 00405B8Ch
  loc_004216C4: push esi
  loc_004216C5: push eax
  loc_004216C6: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004216CC: cmp var_4C, di
  loc_004216D0: jz 00421743h
  loc_004216D2: mov eax, [esi+00000038h]
  loc_004216D5: lea edx, var_28
  loc_004216D8: push edx
  loc_004216D9: lea edx, var_48
  loc_004216DC: mov var_40, ebx
  loc_004216DF: mov var_48, 00004008h
  loc_004216E6: mov ecx, [eax]
  loc_004216E8: push edx
  loc_004216E9: push eax
  loc_004216EA: call [ecx+0000001Ch]
  loc_004216ED: cmp eax, edi
  loc_004216EF: fnclex
  loc_004216F1: jge 00421705h
  loc_004216F3: mov ecx, [esi+00000038h]
  loc_004216F6: push 0000001Ch
  loc_004216F8: push 00408BE8h
  loc_004216FD: push ecx
  loc_004216FE: push eax
  loc_004216FF: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421705: push edi
  loc_00421706: lea edx, var_28
  loc_00421709: push 00408AB0h ; "Value"
  loc_0042170E: lea eax, var_38
  loc_00421711: push edx
  loc_00421712: push eax
  loc_00421713: call [004011B8h] ; __vbaVarLateMemCallLd
  loc_00421719: add esp, 00000010h
  loc_0042171C: push eax
  loc_0042171D: call [00401030h] ; __vbaStrVarMove
  loc_00421723: mov edx, eax
  loc_00421725: lea ecx, var_18
  loc_00421728: call [004011D0h] ; __vbaStrMove
  loc_0042172E: lea ecx, var_38
  loc_00421731: lea edx, var_28
  loc_00421734: push ecx
  loc_00421735: push edx
  loc_00421736: push 00000002h
  loc_00421738: call [00401038h] ; __vbaFreeVarList
  loc_0042173E: add esp, 0000000Ch
  loc_00421741: jmp 0042174Eh
  loc_00421743: xor edx, edx
  loc_00421745: lea ecx, var_18
  loc_00421748: call [00401178h] ; __vbaStrCopy
  loc_0042174E: push 00421779h
  loc_00421753: jmp 00421778h
  loc_00421755: test var_4, 04h
  loc_00421759: jz 00421764h
  loc_0042175B: lea ecx, var_18
  loc_0042175E: call [004011F4h] ; __vbaFreeStr
  loc_00421764: lea eax, var_38
  loc_00421767: lea ecx, var_28
  loc_0042176A: push eax
  loc_0042176B: push ecx
  loc_0042176C: push 00000002h
  loc_0042176E: call [00401038h] ; __vbaFreeVarList
  loc_00421774: add esp, 0000000Ch
  loc_00421777: ret
  loc_00421778: ret
  loc_00421779: mov eax, Me
  loc_0042177C: push eax
  loc_0042177D: mov edx, [eax]
  loc_0042177F: call [edx+00000008h]
  loc_00421782: mov eax, arg_10
  loc_00421785: mov ecx, var_18
  loc_00421788: mov [eax], ecx
  loc_0042178A: mov eax, var_4
  loc_0042178D: mov ecx, var_14
  loc_00421790: pop edi
  loc_00421791: pop esi
  loc_00421792: mov fs:[00000000h], ecx
  loc_00421799: pop ebx
  loc_0042179A: mov esp, ebp
  loc_0042179C: pop ebp
  loc_0042179D: retn 000Ch
End Function

Public Sub Remove(Tag) '4217A0
  loc_004217A0: push ebp
  loc_004217A1: mov ebp, esp
  loc_004217A3: sub esp, 0000000Ch
  loc_004217A6: push 00401AA6h ; __vbaExceptHandler
  loc_004217AB: mov eax, fs:[00000000h]
  loc_004217B1: push eax
  loc_004217B2: mov fs:[00000000h], esp
  loc_004217B9: sub esp, 00000020h
  loc_004217BC: push ebx
  loc_004217BD: push esi
  loc_004217BE: push edi
  loc_004217BF: mov var_C, esp
  loc_004217C2: mov var_8, 00401A60h
  loc_004217C9: xor ebx, ebx
  loc_004217CB: mov var_4, ebx
  loc_004217CE: mov esi, Me
  loc_004217D1: push esi
  loc_004217D2: mov eax, [esi]
  loc_004217D4: call [eax+00000004h]
  loc_004217D7: mov edi, Tag
  loc_004217DA: mov ecx, [esi]
  loc_004217DC: lea edx, var_28
  loc_004217DF: mov var_24, ebx
  loc_004217E2: push edx
  loc_004217E3: push edi
  loc_004217E4: push esi
  loc_004217E5: mov var_28, ebx
  loc_004217E8: call [ecx+00000028h]
  loc_004217EB: cmp eax, ebx
  loc_004217ED: jge 004217FEh
  loc_004217EF: push 00000028h
  loc_004217F1: push 00405B8Ch
  loc_004217F6: push esi
  loc_004217F7: push eax
  loc_004217F8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004217FE: cmp var_28, bx
  loc_00421802: jz 00421833h
  loc_00421804: mov eax, [esi+00000038h]
  loc_00421807: lea edx, var_24
  loc_0042180A: mov var_1C, edi
  loc_0042180D: mov var_24, 00004008h
  loc_00421814: mov ecx, [eax]
  loc_00421816: push edx
  loc_00421817: push eax
  loc_00421818: call [ecx+00000028h]
  loc_0042181B: cmp eax, ebx
  loc_0042181D: fnclex
  loc_0042181F: jge 00421833h
  loc_00421821: mov ecx, [esi+00000038h]
  loc_00421824: push 00000028h
  loc_00421826: push 00408BE8h
  loc_0042182B: push ecx
  loc_0042182C: push eax
  loc_0042182D: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421833: mov eax, Me
  loc_00421836: push eax
  loc_00421837: mov edx, [eax]
  loc_00421839: call [edx+00000008h]
  loc_0042183C: mov eax, var_4
  loc_0042183F: mov ecx, var_14
  loc_00421842: pop edi
  loc_00421843: pop esi
  loc_00421844: mov fs:[00000000h], ecx
  loc_0042184B: pop ebx
  loc_0042184C: mov esp, ebp
  loc_0042184E: pop ebp
  loc_0042184F: retn 0008h
End Sub

Public Function Add(Tag, Value) '421860
  loc_00421860: push ebp
  loc_00421861: mov ebp, esp
  loc_00421863: sub esp, 0000000Ch
  loc_00421866: push 00401AA6h ; __vbaExceptHandler
  loc_0042186B: mov eax, fs:[00000000h]
  loc_00421871: push eax
  loc_00421872: mov fs:[00000000h], esp
  loc_00421879: sub esp, 00000078h
  loc_0042187C: push ebx
  loc_0042187D: push esi
  loc_0042187E: push edi
  loc_0042187F: mov var_C, esp
  loc_00421882: mov var_8, 00401A68h
  loc_00421889: xor ebx, ebx
  loc_0042188B: mov var_4, ebx
  loc_0042188E: mov esi, Me
  loc_00421891: push esi
  loc_00421892: mov eax, [esi]
  loc_00421894: call [eax+00000004h]
  loc_00421897: mov ecx, arg_14
  loc_0042189A: mov edi, Tag
  loc_0042189D: push edi
  loc_0042189E: push esi
  loc_0042189F: mov [ecx], ebx
  loc_004218A1: mov edx, [esi]
  loc_004218A3: mov var_18, ebx
  loc_004218A6: mov var_1C, ebx
  loc_004218A9: mov var_20, ebx
  loc_004218AC: mov var_30, ebx
  loc_004218AF: mov var_40, ebx
  loc_004218B2: mov var_50, ebx
  loc_004218B5: mov var_60, ebx
  loc_004218B8: call [edx+00000030h]
  loc_004218BB: cmp eax, ebx
  loc_004218BD: jge 004218CEh
  loc_004218BF: push 00000030h
  loc_004218C1: push 00405B8Ch
  loc_004218C6: push esi
  loc_004218C7: push eax
  loc_004218C8: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004218CE: push 00401FD4h
  loc_004218D3: call [00401110h] ; __vbaNew
  loc_004218D9: push eax
  loc_004218DA: lea eax, var_1C
  loc_004218DD: push eax
  loc_004218DE: call [00401080h] ; __vbaObjSet
  loc_004218E4: mov eax, var_1C
  loc_004218E7: mov edx, [edi]
  loc_004218E9: push edx
  loc_004218EA: push eax
  loc_004218EB: mov ecx, [eax]
  loc_004218ED: call [ecx+00000020h]
  loc_004218F0: cmp eax, ebx
  loc_004218F2: fnclex
  loc_004218F4: jge 00421908h
  loc_004218F6: mov ecx, var_1C
  loc_004218F9: push 00000020h
  loc_004218FB: push 00408BB4h
  loc_00421900: push ecx
  loc_00421901: push eax
  loc_00421902: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421908: mov ecx, Value
  loc_0042190B: mov eax, var_1C
  loc_0042190E: mov ecx, [ecx]
  loc_00421910: mov edx, [eax]
  loc_00421912: push ecx
  loc_00421913: push eax
  loc_00421914: call [edx+00000028h]
  loc_00421917: cmp eax, ebx
  loc_00421919: fnclex
  loc_0042191B: jge 0042192Fh
  loc_0042191D: mov edx, var_1C
  loc_00421920: push 00000028h
  loc_00421922: push 00408BB4h
  loc_00421927: push edx
  loc_00421928: push eax
  loc_00421929: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0042192F: mov eax, 0000000Ah
  loc_00421934: mov ecx, 80020004h
  loc_00421939: mov var_40, eax
  loc_0042193C: mov var_30, eax
  loc_0042193F: mov eax, var_1C
  loc_00421942: mov var_38, ecx
  loc_00421945: mov var_28, ecx
  loc_00421948: lea ecx, var_20
  loc_0042194B: mov var_58, edi
  loc_0042194E: mov edi, [00401094h] ; __vbaObjSetAddref
  loc_00421954: push eax
  loc_00421955: push ecx
  loc_00421956: mov var_60, 00004008h
  loc_0042195D: call edi
  loc_0042195F: lea edx, var_20
  loc_00421962: mov eax, [esi+00000038h]
  loc_00421965: mov var_48, edx
  loc_00421968: lea edx, var_40
  loc_0042196B: push edx
  loc_0042196C: lea edx, var_30
  loc_0042196F: push edx
  loc_00421970: lea edx, var_60
  loc_00421973: push edx
  loc_00421974: lea edx, var_50
  loc_00421977: mov var_50, 00004009h
  loc_0042197E: mov ecx, [eax]
  loc_00421980: push edx
  loc_00421981: push eax
  loc_00421982: call [ecx+00000020h]
  loc_00421985: cmp eax, ebx
  loc_00421987: fnclex
  loc_00421989: jge 0042199Dh
  loc_0042198B: mov ecx, [esi+00000038h]
  loc_0042198E: push 00000020h
  loc_00421990: push 00408BE8h
  loc_00421995: push ecx
  loc_00421996: push eax
  loc_00421997: call [0040105Ch] ; __vbaHresultCheckObj
  loc_0042199D: mov edx, var_20
  loc_004219A0: push 00408BB4h
  loc_004219A5: push edx
  loc_004219A6: call [004011D4h] ; __vbaCastObj
  loc_004219AC: push eax
  loc_004219AD: lea eax, var_1C
  loc_004219B0: push eax
  loc_004219B1: call [00401080h] ; __vbaObjSet
  loc_004219B7: lea ecx, var_20
  loc_004219BA: call [004011F0h] ; __vbaFreeObj
  loc_004219C0: lea ecx, var_40
  loc_004219C3: lea edx, var_30
  loc_004219C6: push ecx
  loc_004219C7: push edx
  loc_004219C8: push 00000002h
  loc_004219CA: call [00401038h] ; __vbaFreeVarList
  loc_004219D0: mov eax, var_1C
  loc_004219D3: add esp, 0000000Ch
  loc_004219D6: lea ecx, var_18
  loc_004219D9: push eax
  loc_004219DA: push ecx
  loc_004219DB: call edi
  loc_004219DD: push 00421A1Ah
  loc_004219E2: jmp 00421A10h
  loc_004219E4: test var_4, 04h
  loc_004219E8: jz 004219F3h
  loc_004219EA: lea ecx, var_18
  loc_004219ED: call [004011F0h] ; __vbaFreeObj
  loc_004219F3: lea ecx, var_20
  loc_004219F6: call [004011F0h] ; __vbaFreeObj
  loc_004219FC: lea edx, var_40
  loc_004219FF: lea eax, var_30
  loc_00421A02: push edx
  loc_00421A03: push eax
  loc_00421A04: push 00000002h
  loc_00421A06: call [00401038h] ; __vbaFreeVarList
  loc_00421A0C: add esp, 0000000Ch
  loc_00421A0F: ret
  loc_00421A10: lea ecx, var_1C
  loc_00421A13: call [004011F0h] ; __vbaFreeObj
  loc_00421A19: ret
  loc_00421A1A: mov eax, Me
  loc_00421A1D: push eax
  loc_00421A1E: mov ecx, [eax]
  loc_00421A20: call [ecx+00000008h]
  loc_00421A23: mov edx, arg_14
  loc_00421A26: mov eax, var_18
  loc_00421A29: mov [edx], eax
  loc_00421A2B: mov eax, var_4
  loc_00421A2E: mov ecx, var_14
  loc_00421A31: pop edi
  loc_00421A32: pop esi
  loc_00421A33: mov fs:[00000000h], ecx
  loc_00421A3A: pop ebx
  loc_00421A3B: mov esp, ebp
  loc_00421A3D: pop ebp
  loc_00421A3E: retn 0010h
End Function

Public Property Let Text(Value) '421A50
  loc_00421A50: push ebp
  loc_00421A51: mov ebp, esp
  loc_00421A53: sub esp, 0000000Ch
  loc_00421A56: push 00401AA6h ; __vbaExceptHandler
  loc_00421A5B: mov eax, fs:[00000000h]
  loc_00421A61: push eax
  loc_00421A62: mov fs:[00000000h], esp
  loc_00421A69: sub esp, 00000098h
  loc_00421A6F: push ebx
  loc_00421A70: push esi
  loc_00421A71: push edi
  loc_00421A72: mov var_C, esp
  loc_00421A75: mov var_8, 00401A78h
  loc_00421A7C: xor ebx, ebx
  loc_00421A7E: mov var_4, ebx
  loc_00421A81: mov esi, Me
  loc_00421A84: push esi
  loc_00421A85: mov eax, [esi]
  loc_00421A87: call [eax+00000004h]
  loc_00421A8A: mov edx, Value
  loc_00421A8D: push ebx
  loc_00421A8E: lea ecx, var_88
  loc_00421A94: push FFFFFFFFh
  loc_00421A96: mov eax, [edx]
  loc_00421A98: push ecx
  loc_00421A99: lea ecx, var_58
  loc_00421A9C: add esi, 00000034h
  loc_00421A9F: push eax
  loc_00421AA0: mov var_88, ebx
  loc_00421AA6: push ecx
  loc_00421AA7: mov var_18, ebx
  loc_00421AAA: mov var_28, ebx
  loc_00421AAD: mov var_38, ebx
  loc_00421AB0: mov var_3C, ebx
  loc_00421AB3: mov var_40, ebx
  loc_00421AB6: mov var_44, ebx
  loc_00421AB9: mov var_48, ebx
  loc_00421ABC: mov var_58, ebx
  loc_00421ABF: mov var_68, ebx
  loc_00421AC2: mov var_78, ebx
  loc_00421AC5: mov var_98, ebx
  loc_00421ACB: mov var_80, esi
  loc_00421ACE: mov var_88, 00004008h
  loc_00421AD8: call [00401124h] ; rtcSplit
  loc_00421ADE: lea edx, var_58
  loc_00421AE1: lea ecx, var_28
  loc_00421AE4: call [00401014h] ; __vbaVarMove
  loc_00421AEA: mov esi, [004010ACh] ; __vbaRefVarAry
  loc_00421AF0: lea edx, var_28
  loc_00421AF3: push edx
  loc_00421AF4: call __vbaRefVarAry
  loc_00421AF6: mov eax, [eax]
  loc_00421AF8: push eax
  loc_00421AF9: push 00000001h
  loc_00421AFB: call [00401144h] ; __vbaUbound
  loc_00421B01: mov edi, [004010ECh] ; __vbaI2I4
  loc_00421B07: mov ecx, eax
  loc_00421B09: call edi
  loc_00421B0B: lea ecx, var_28
  loc_00421B0E: mov var_A4, eax
  loc_00421B14: push ecx
  loc_00421B15: call __vbaRefVarAry
  loc_00421B17: mov edx, [eax]
  loc_00421B19: push edx
  loc_00421B1A: push 00000001h
  loc_00421B1C: call [004010F8h] ; __vbaLbound
  loc_00421B22: mov ecx, eax
  loc_00421B24: call edi
  loc_00421B26: mov edi, [0040109Ch] ; __vbaVarIndexLoad
  loc_00421B2C: mov var_18, eax
  loc_00421B2F: cmp ax, var_A4
  loc_00421B36: jg 00421D14h
  loc_00421B3C: sub esp, 00000010h
  loc_00421B3F: mov ecx, 00004002h
  loc_00421B44: mov edx, esp
  loc_00421B46: mov var_88, ecx
  loc_00421B4C: lea eax, var_18
  loc_00421B4F: push 00000001h
  loc_00421B51: mov [edx], ecx
  loc_00421B53: mov ecx, var_84
  loc_00421B59: mov var_80, eax
  loc_00421B5C: mov [edx+00000004h], ecx
  loc_00421B5F: lea ecx, var_28
  loc_00421B62: push ecx
  loc_00421B63: mov [edx+00000008h], eax
  loc_00421B66: mov eax, var_7C
  loc_00421B69: mov [edx+0000000Ch], eax
  loc_00421B6C: lea edx, var_58
  loc_00421B6F: push edx
  loc_00421B70: call edi
  loc_00421B72: add esp, 0000001Ch
  loc_00421B75: lea edx, var_98
  loc_00421B7B: lea ecx, var_68
  loc_00421B7E: mov var_90, 00408C0Ch
  loc_00421B88: mov var_98, 00000008h
  loc_00421B92: call [004011B4h] ; __vbaVarDup
  loc_00421B98: push ebx
  loc_00421B99: lea eax, var_68
  loc_00421B9C: push FFFFFFFFh
  loc_00421B9E: lea ecx, var_58
  loc_00421BA1: push eax
  loc_00421BA2: lea edx, var_44
  loc_00421BA5: push ecx
  loc_00421BA6: push edx
  loc_00421BA7: call [00401148h] ; __vbaStrVarVal
  loc_00421BAD: push eax
  loc_00421BAE: lea eax, var_78
  loc_00421BB1: push eax
  loc_00421BB2: call [00401124h] ; rtcSplit
  loc_00421BB8: lea edx, var_78
  loc_00421BBB: lea ecx, var_38
  loc_00421BBE: call [00401014h] ; __vbaVarMove
  loc_00421BC4: lea ecx, var_44
  loc_00421BC7: call [004011F4h] ; __vbaFreeStr
  loc_00421BCD: lea ecx, var_68
  loc_00421BD0: lea edx, var_58
  loc_00421BD3: push ecx
  loc_00421BD4: push edx
  loc_00421BD5: push 00000002h
  loc_00421BD7: call [00401038h] ; __vbaFreeVarList
  loc_00421BDD: add esp, 0000000Ch
  loc_00421BE0: lea eax, var_38
  loc_00421BE3: push eax
  loc_00421BE4: call __vbaRefVarAry
  loc_00421BE6: mov ecx, [eax]
  loc_00421BE8: push ecx
  loc_00421BE9: push 00000001h
  loc_00421BEB: call [004010F8h] ; __vbaLbound
  loc_00421BF1: lea edx, var_38
  loc_00421BF4: mov ebx, eax
  loc_00421BF6: push edx
  loc_00421BF7: call __vbaRefVarAry
  loc_00421BF9: mov eax, [eax]
  loc_00421BFB: push eax
  loc_00421BFC: push 00000001h
  loc_00421BFE: call [00401144h] ; __vbaUbound
  loc_00421C04: cmp eax, ebx
  loc_00421C06: jle 00421CFFh ; Unknown_E845897B()
  loc_00421C0C: lea ecx, var_38
  loc_00421C0F: push ecx
  loc_00421C10: call __vbaRefVarAry
  loc_00421C12: mov edx, [eax]
  loc_00421C14: push edx
  loc_00421C15: push 00000001h
  loc_00421C17: call [004010F8h] ; __vbaLbound
  loc_00421C1D: sub esp, 00000010h
  loc_00421C20: mov ecx, 00000003h
  loc_00421C25: mov edx, esp
  loc_00421C27: mov var_88, ecx
  loc_00421C2D: mov var_80, eax
  loc_00421C30: push 00000001h
  loc_00421C32: mov [edx], ecx
  loc_00421C34: mov ecx, var_84
  loc_00421C3A: mov [edx+00000004h], ecx
  loc_00421C3D: lea ecx, var_38
  loc_00421C40: push ecx
  loc_00421C41: mov [edx+00000008h], eax
  loc_00421C44: mov eax, var_7C
  loc_00421C47: mov [edx+0000000Ch], eax
  loc_00421C4A: lea edx, var_58
  loc_00421C4D: push edx
  loc_00421C4E: call edi
  loc_00421C50: add esp, 0000001Ch
  loc_00421C53: push eax
  loc_00421C54: call [00401030h] ; __vbaStrVarMove
  loc_00421C5A: mov ebx, [004011D0h] ; __vbaStrMove
  loc_00421C60: mov edx, eax
  loc_00421C62: lea ecx, var_40
  loc_00421C65: call ebx
  loc_00421C67: lea ecx, var_58
  loc_00421C6A: call [00401020h] ; __vbaFreeVar
  loc_00421C70: lea eax, var_38
  loc_00421C73: push eax
  loc_00421C74: call __vbaRefVarAry
  loc_00421C76: mov ecx, [eax]
  loc_00421C78: push ecx
  loc_00421C79: push 00000001h
  loc_00421C7B: call [00401144h] ; __vbaUbound
  loc_00421C81: sub esp, 00000010h
  loc_00421C84: mov ecx, 00000003h
  loc_00421C89: mov edx, esp
  loc_00421C8B: mov var_88, ecx
  loc_00421C91: mov var_80, eax
  loc_00421C94: push 00000001h
  loc_00421C96: mov [edx], ecx
  loc_00421C98: mov ecx, var_84
  loc_00421C9E: mov [edx+00000004h], ecx
  loc_00421CA1: lea ecx, var_38
  loc_00421CA4: push ecx
  loc_00421CA5: mov [edx+00000008h], eax
  loc_00421CA8: mov eax, var_7C
  loc_00421CAB: mov [edx+0000000Ch], eax
  loc_00421CAE: lea edx, var_58
  loc_00421CB1: push edx
  loc_00421CB2: call edi
  loc_00421CB4: add esp, 0000001Ch
  loc_00421CB7: push eax
  loc_00421CB8: call [00401030h] ; __vbaStrVarMove
  loc_00421CBE: mov edx, eax
  loc_00421CC0: lea ecx, var_3C
  loc_00421CC3: call ebx
  loc_00421CC5: lea ecx, var_58
  loc_00421CC8: call [00401020h] ; __vbaFreeVar
  loc_00421CCE: mov ebx, Me
  loc_00421CD1: lea ecx, var_48
  loc_00421CD4: push ecx
  loc_00421CD5: lea edx, var_3C
  loc_00421CD8: mov eax, [ebx]
  loc_00421CDA: lea ecx, var_40
  loc_00421CDD: push edx
  loc_00421CDE: push ecx
  loc_00421CDF: push ebx
  loc_00421CE0: call [eax+00000034h]
  loc_00421CE3: test eax, eax
  loc_00421CE5: jge 00421CF6h
  loc_00421CE7: push 00000034h
  loc_00421CE9: push 00405B8Ch
  loc_00421CEE: push ebx
  loc_00421CEF: push eax
  loc_00421CF0: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421CF6: lea ecx, var_48
  loc_00421CF9: call [004011F0h] ; __vbaFreeObj
  loc_00421CFF: mov eax, 00000001h
  loc_00421D04: add ax, var_18
  loc_00421D08: jo 00421D85h
  loc_00421D0A: mov var_18, eax
  loc_00421D0D: xor ebx, ebx
  loc_00421D0F: jmp 00421B2Fh
  loc_00421D14: push 00421D66h
  loc_00421D19: jmp 00421D45h
  loc_00421D1B: lea ecx, var_44
  loc_00421D1E: call [004011F4h] ; __vbaFreeStr
  loc_00421D24: lea ecx, var_48
  loc_00421D27: call [004011F0h] ; __vbaFreeObj
  loc_00421D2D: lea edx, var_78
  loc_00421D30: lea eax, var_68
  loc_00421D33: push edx
  loc_00421D34: lea ecx, var_58
  loc_00421D37: push eax
  loc_00421D38: push ecx
  loc_00421D39: push 00000003h
  loc_00421D3B: call [00401038h] ; __vbaFreeVarList
  loc_00421D41: add esp, 00000010h
  loc_00421D44: ret
  loc_00421D45: mov esi, [00401020h] ; __vbaFreeVar
  loc_00421D4B: lea ecx, var_28
  loc_00421D4E: call __vbaFreeVar
  loc_00421D50: lea ecx, var_38
  loc_00421D53: call __vbaFreeVar
  loc_00421D55: mov esi, [004011F4h] ; __vbaFreeStr
  loc_00421D5B: lea ecx, var_3C
  loc_00421D5E: call __vbaFreeStr
  loc_00421D60: lea ecx, var_40
  loc_00421D63: call __vbaFreeStr
  loc_00421D65: ret
  loc_00421D66: mov eax, Me
  loc_00421D69: push eax
  loc_00421D6A: mov edx, [eax]
  loc_00421D6C: call [edx+00000008h]
  loc_00421D6F: mov eax, var_4
  loc_00421D72: mov ecx, var_14
  loc_00421D75: pop edi
  loc_00421D76: pop esi
  loc_00421D77: mov fs:[00000000h], ecx
  loc_00421D7E: pop ebx
  loc_00421D7F: mov esp, ebp
  loc_00421D81: pop ebp
  loc_00421D82: retn 0008h
End Sub

Public Property Get Text(arg_C) '421D90
  loc_00421D90: push ebp
  loc_00421D91: mov ebp, esp
  loc_00421D93: sub esp, 0000000Ch
  loc_00421D96: push 00401AA6h ; __vbaExceptHandler
  loc_00421D9B: mov eax, fs:[00000000h]
  loc_00421DA1: push eax
  loc_00421DA2: mov fs:[00000000h], esp
  loc_00421DA9: sub esp, 00000058h
  loc_00421DAC: push ebx
  loc_00421DAD: push esi
  loc_00421DAE: push edi
  loc_00421DAF: mov var_C, esp
  loc_00421DB2: mov var_8, 00401A88h
  loc_00421DB9: xor ebx, ebx
  loc_00421DBB: mov var_4, ebx
  loc_00421DBE: mov esi, Me
  loc_00421DC1: push esi
  loc_00421DC2: mov eax, [esi]
  loc_00421DC4: call [eax+00000004h]
  loc_00421DC7: mov ecx, arg_C
  loc_00421DCA: lea eax, var_20
  loc_00421DCD: mov var_18, ebx
  loc_00421DD0: mov var_1C, ebx
  loc_00421DD3: mov [ecx], ebx
  loc_00421DD5: mov edx, [esi+00000038h]
  loc_00421DD8: push edx
  loc_00421DD9: lea ecx, var_60
  loc_00421DDC: push eax
  loc_00421DDD: push ecx
  loc_00421DDE: push 00408BB4h
  loc_00421DE3: mov var_20, ebx
  loc_00421DE6: mov var_24, ebx
  loc_00421DE9: mov var_28, ebx
  loc_00421DEC: mov var_2C, ebx
  loc_00421DEF: mov var_30, ebx
  loc_00421DF2: mov var_34, ebx
  loc_00421DF5: mov var_44, ebx
  loc_00421DF8: mov var_60, ebx
  loc_00421DFB: call [00401078h] ; __vbaForEachCollObj
  loc_00421E01: mov esi, [004011D0h] ; __vbaStrMove
  loc_00421E07: mov edi, [00401050h] ; __vbaStrCat
  loc_00421E0D: cmp eax, ebx
  loc_00421E0F: jz 00421F21h
  loc_00421E15: mov eax, var_20
  loc_00421E18: lea ecx, var_24
  loc_00421E1B: push ecx
  loc_00421E1C: push eax
  loc_00421E1D: mov edx, [eax]
  loc_00421E1F: call [edx+0000001Ch]
  loc_00421E22: cmp eax, ebx
  loc_00421E24: fnclex
  loc_00421E26: jge 00421E3Ah
  loc_00421E28: mov edx, var_20
  loc_00421E2B: push 0000001Ch
  loc_00421E2D: push 00408BB4h
  loc_00421E32: push edx
  loc_00421E33: push eax
  loc_00421E34: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421E3A: mov eax, var_24
  loc_00421E3D: push eax
  loc_00421E3E: call [0040102Ch] ; __vbaLenBstr
  loc_00421E44: xor ebx, ebx
  loc_00421E46: lea ecx, var_24
  loc_00421E49: test eax, eax
  loc_00421E4B: setg bl
  loc_00421E4E: neg ebx
  loc_00421E50: call [004011F4h] ; __vbaFreeStr
  loc_00421E56: test bx, bx
  loc_00421E59: jz 00421F07h
  loc_00421E5F: mov eax, var_20
  loc_00421E62: lea edx, var_24
  loc_00421E65: push edx
  loc_00421E66: push eax
  loc_00421E67: mov ecx, [eax]
  loc_00421E69: call [ecx+0000001Ch]
  loc_00421E6C: test eax, eax
  loc_00421E6E: fnclex
  loc_00421E70: jge 00421E84h
  loc_00421E72: mov ecx, var_20
  loc_00421E75: push 0000001Ch
  loc_00421E77: push 00408BB4h
  loc_00421E7C: push ecx
  loc_00421E7D: push eax
  loc_00421E7E: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421E84: mov eax, var_20
  loc_00421E87: lea ecx, var_30
  loc_00421E8A: push ecx
  loc_00421E8B: push eax
  loc_00421E8C: mov edx, [eax]
  loc_00421E8E: call [edx+00000024h]
  loc_00421E91: test eax, eax
  loc_00421E93: fnclex
  loc_00421E95: jge 00421EA9h
  loc_00421E97: mov edx, var_20
  loc_00421E9A: push 00000024h
  loc_00421E9C: push 00408BB4h
  loc_00421EA1: push edx
  loc_00421EA2: push eax
  loc_00421EA3: call [0040105Ch] ; __vbaHresultCheckObj
  loc_00421EA9: mov ecx, Me
  loc_00421EAC: mov eax, var_18
  loc_00421EAF: push eax
  loc_00421EB0: mov edx, [ecx+00000034h]
  loc_00421EB3: push edx
  loc_00421EB4: call edi
  loc_00421EB6: mov edx, eax
  loc_00421EB8: lea ecx, var_28
  loc_00421EBB: call __vbaStrMove
  loc_00421EBD: push eax
  loc_00421EBE: mov eax, var_24
  loc_00421EC1: push eax
  loc_00421EC2: call edi
  loc_00421EC4: mov edx, eax
  loc_00421EC6: lea ecx, var_2C
  loc_00421EC9: call __vbaStrMove
  loc_00421ECB: push eax
  loc_00421ECC: push 00408C0Ch
  loc_00421ED1: call edi
  loc_00421ED3: mov edx, eax
  loc_00421ED5: lea ecx, var_34
  loc_00421ED8: call __vbaStrMove
  loc_00421EDA: mov ecx, var_30
  loc_00421EDD: push eax
  loc_00421EDE: push ecx
  loc_00421EDF: call edi
  loc_00421EE1: mov edx, eax
  loc_00421EE3: lea ecx, var_18
  loc_00421EE6: call __vbaStrMove
  loc_00421EE8: lea edx, var_30
  loc_00421EEB: lea eax, var_34
  loc_00421EEE: push edx
  loc_00421EEF: lea ecx, var_2C
  loc_00421EF2: push eax
  loc_00421EF3: lea edx, var_24
  loc_00421EF6: push ecx
  loc_00421EF7: lea eax, var_28
  loc_00421EFA: push edx
  loc_00421EFB: push eax
  loc_00421EFC: push 00000005h
  loc_00421EFE: call [00401180h] ; __vbaFreeStrList
  loc_00421F04: add esp, 00000018h
  loc_00421F07: lea ecx, var_20
  loc_00421F0A: lea edx, var_60
  loc_00421F0D: push ecx
  loc_00421F0E: push edx
  loc_00421F0F: push 00408BB4h
  loc_00421F14: call [004010C0h] ; __vbaNextEachCollObj
  loc_00421F1A: xor ebx, ebx
  loc_00421F1C: jmp 00421E0Dh
  loc_00421F21: mov eax, Me
  loc_00421F24: mov edi, [0040102Ch] ; __vbaLenBstr
  loc_00421F2A: mov ecx, [eax+00000034h]
  loc_00421F2D: push ecx
  loc_00421F2E: call edi
  loc_00421F30: mov edx, var_18
  loc_00421F33: mov ebx, eax
  loc_00421F35: push edx
  loc_00421F36: call edi
  loc_00421F38: cmp eax, ebx
  loc_00421F3A: jle 00421F7Bh
  loc_00421F3C: mov ecx, Me
  loc_00421F3F: lea eax, var_44
  loc_00421F42: push eax
  loc_00421F43: mov var_3C, 80020004h
  loc_00421F4A: mov edx, [ecx+00000034h]
  loc_00421F4D: mov var_44, 0000000Ah
  loc_00421F54: push edx
  loc_00421F55: call edi
  loc_00421F57: add eax, 00000001h
  loc_00421F5A: jo 00422007h
  loc_00421F60: push eax
  loc_00421F61: mov eax, var_18
  loc_00421F64: push eax
  loc_00421F65: call [004010B8h] ; rtcMidCharBstr
  loc_00421F6B: mov edx, eax
  loc_00421F6D: lea ecx, var_18
  loc_00421F70: call __vbaStrMove
  loc_00421F72: lea ecx, var_44
  loc_00421F75: call [00401020h] ; __vbaFreeVar
  loc_00421F7B: mov edx, var_18
  loc_00421F7E: lea ecx, var_1C
  loc_00421F81: call [00401178h] ; __vbaStrCopy
  loc_00421F87: push 00421FE0h
  loc_00421F8C: jmp 00421FC6h
  loc_00421F8E: test var_4, 04h
  loc_00421F92: jz 00421F9Dh
  loc_00421F94: lea ecx, var_1C
  loc_00421F97: call [004011F4h] ; __vbaFreeStr
  loc_00421F9D: lea ecx, var_34
  loc_00421FA0: lea edx, var_30
  loc_00421FA3: push ecx
  loc_00421FA4: lea eax, var_2C
  loc_00421FA7: push edx
  loc_00421FA8: lea ecx, var_28
  loc_00421FAB: push eax
  loc_00421FAC: lea edx, var_24
  loc_00421FAF: push ecx
  loc_00421FB0: push edx
  loc_00421FB1: push 00000005h
  loc_00421FB3: call [00401180h] ; __vbaFreeStrList
  loc_00421FB9: add esp, 00000018h
  loc_00421FBC: lea ecx, var_44
  loc_00421FBF: call [00401020h] ; __vbaFreeVar
  loc_00421FC5: ret
  loc_00421FC6: mov esi, [004011F0h] ; __vbaFreeObj
  loc_00421FCC: lea ecx, var_60
  loc_00421FCF: call __vbaFreeObj
  loc_00421FD1: lea ecx, var_18
  loc_00421FD4: call [004011F4h] ; __vbaFreeStr
  loc_00421FDA: lea ecx, var_20
  loc_00421FDD: call __vbaFreeObj
  loc_00421FDF: ret
  loc_00421FE0: mov eax, Me
  loc_00421FE3: push eax
  loc_00421FE4: mov ecx, [eax]
  loc_00421FE6: call [ecx+00000008h]
  loc_00421FE9: mov edx, arg_C
  loc_00421FEC: mov eax, var_1C
  loc_00421FEF: mov [edx], eax
  loc_00421FF1: mov eax, var_4
  loc_00421FF4: mov ecx, var_14
  loc_00421FF7: pop edi
  loc_00421FF8: pop esi
  loc_00421FF9: mov fs:[00000000h], ecx
  loc_00422000: pop ebx
  loc_00422001: mov esp, ebp
  loc_00422003: pop ebp
  loc_00422004: retn 0008h
End Sub

Private Sub Proc_5_9_420E60() '420E60
  loc_00420E60: push ebp
  loc_00420E61: mov ebp, esp
  loc_00420E63: sub esp, 0000000Ch
  loc_00420E66: push 00401AA6h ; __vbaExceptHandler
  loc_00420E6B: mov eax, fs:[00000000h]
  loc_00420E71: push eax
  loc_00420E72: mov fs:[00000000h], esp
  loc_00420E79: sub esp, 0000000Ch
  loc_00420E7C: push ebx
  loc_00420E7D: push esi
  loc_00420E7E: push edi
  loc_00420E7F: mov var_C, esp
  loc_00420E82: mov var_8, 004019C8h
  loc_00420E89: mov esi, Me
  loc_00420E8C: mov eax, esi
  loc_00420E8E: and eax, 00000001h
  loc_00420E91: mov var_4, eax
  loc_00420E94: and esi, FFFFFFFEh
  loc_00420E97: push esi
  loc_00420E98: mov Me, esi
  loc_00420E9B: mov ecx, [esi]
  loc_00420E9D: call [ecx+00000004h]
  loc_00420EA0: xor edi, edi
  loc_00420EA2: mov edx, 00406D40h
  loc_00420EA7: lea ecx, [esi+00000034h]
  loc_00420EAA: mov var_18, edi
  loc_00420EAD: call [00401178h] ; __vbaStrCopy
  loc_00420EB3: push 00408BF8h
  loc_00420EB8: call [00401110h] ; __vbaNew
  loc_00420EBE: lea edx, var_18
  loc_00420EC1: push eax
  loc_00420EC2: push edx
  loc_00420EC3: call [00401080h] ; __vbaObjSet
  loc_00420EC9: add esi, 00000038h
  loc_00420ECC: push eax
  loc_00420ECD: push esi
  loc_00420ECE: call [00401094h] ; __vbaObjSetAddref
  loc_00420ED4: lea ecx, var_18
  loc_00420ED7: call [004011F0h] ; __vbaFreeObj
  loc_00420EDD: mov var_4, edi
  loc_00420EE0: push 00420EF2h
  loc_00420EE5: jmp 00420EF1h
  loc_00420EE7: lea ecx, var_18
  loc_00420EEA: call [004011F0h] ; __vbaFreeObj
  loc_00420EF0: ret
  loc_00420EF1: ret
  loc_00420EF2: mov eax, Me
  loc_00420EF5: push eax
  loc_00420EF6: mov ecx, [eax]
  loc_00420EF8: call [ecx+00000008h]
  loc_00420EFB: mov eax, var_4
  loc_00420EFE: mov ecx, var_14
  loc_00420F01: pop edi
  loc_00420F02: pop esi
  loc_00420F03: mov fs:[00000000h], ecx
  loc_00420F0A: pop ebx
  loc_00420F0B: mov esp, ebp
  loc_00420F0D: pop ebp
  loc_00420F0E: retn 0004h
End Sub

Private Sub Proc_5_10_420F20() '420F20
  loc_00420F20: push ebp
  loc_00420F21: mov ebp, esp
  loc_00420F23: sub esp, 0000000Ch
  loc_00420F26: push 00401AA6h ; __vbaExceptHandler
  loc_00420F2B: mov eax, fs:[00000000h]
  loc_00420F31: push eax
  loc_00420F32: mov fs:[00000000h], esp
  loc_00420F39: sub esp, 0000000Ch
  loc_00420F3C: push ebx
  loc_00420F3D: push esi
  loc_00420F3E: push edi
  loc_00420F3F: mov var_C, esp
  loc_00420F42: mov var_8, 004019D8h
  loc_00420F49: mov esi, Me
  loc_00420F4C: mov eax, esi
  loc_00420F4E: and eax, 00000001h
  loc_00420F51: mov var_4, eax
  loc_00420F54: and esi, FFFFFFFEh
  loc_00420F57: push esi
  loc_00420F58: mov Me, esi
  loc_00420F5B: mov ecx, [esi]
  loc_00420F5D: call [ecx+00000004h]
  loc_00420F60: xor edi, edi
  loc_00420F62: push 00408BE8h
  loc_00420F67: push edi
  loc_00420F68: mov var_18, edi
  loc_00420F6B: call [004011D4h] ; __vbaCastObj
  loc_00420F71: lea edx, var_18
  loc_00420F74: push eax
  loc_00420F75: push edx
  loc_00420F76: call [00401080h] ; __vbaObjSet
  loc_00420F7C: add esi, 00000038h
  loc_00420F7F: push eax
  loc_00420F80: push esi
  loc_00420F81: call [00401094h] ; __vbaObjSetAddref
  loc_00420F87: lea ecx, var_18
  loc_00420F8A: call [004011F0h] ; __vbaFreeObj
  loc_00420F90: mov var_4, edi
  loc_00420F93: push 00420FA5h
  loc_00420F98: jmp 00420FA4h
  loc_00420F9A: lea ecx, var_18
  loc_00420F9D: call [004011F0h] ; __vbaFreeObj
  loc_00420FA3: ret
  loc_00420FA4: ret
  loc_00420FA5: mov eax, Me
  loc_00420FA8: push eax
  loc_00420FA9: mov ecx, [eax]
  loc_00420FAB: call [ecx+00000008h]
  loc_00420FAE: mov eax, var_4
  loc_00420FB1: mov ecx, var_14
  loc_00420FB4: pop edi
  loc_00420FB5: pop esi
  loc_00420FB6: mov fs:[00000000h], ecx
  loc_00420FBD: pop ebx
  loc_00420FBE: mov esp, ebp
  loc_00420FC0: pop ebp
  loc_00420FC1: retn 0004h
End Sub

Private Sub Proc_5_11_421060(arg_C) '421060
  loc_00421060: push ebp
  loc_00421061: mov ebp, esp
  loc_00421063: sub esp, 00000008h
  loc_00421066: push 00401AA6h ; __vbaExceptHandler
  loc_0042106B: mov eax, fs:[00000000h]
  loc_00421071: push eax
  loc_00421072: mov fs:[00000000h], esp
  loc_00421079: sub esp, 00000094h
  loc_0042107F: push ebx
  loc_00421080: push esi
  loc_00421081: push edi
  loc_00421082: mov var_8, esp
  loc_00421085: mov var_4, 004019F0h
  loc_0042108C: mov edi, Me
  loc_0042108F: xor eax, eax
  loc_00421091: mov var_14, eax
  loc_00421094: mov var_24, eax
  loc_00421097: mov var_34, eax
  loc_0042109A: mov var_38, eax
  loc_0042109D: mov var_3C, eax
  loc_004210A0: mov var_40, eax
  loc_004210A3: mov var_44, eax
  loc_004210A6: mov var_54, eax
  loc_004210A9: mov var_64, eax
  loc_004210AC: mov var_74, eax
  loc_004210AF: mov var_94, eax
  loc_004210B5: push eax
  loc_004210B6: mov eax, arg_C
  loc_004210B9: lea ecx, [edi+00000034h]
  loc_004210BC: lea edx, var_84
  loc_004210C2: mov var_7C, ecx
  loc_004210C5: mov ecx, [eax]
  loc_004210C7: push FFFFFFFFh
  loc_004210C9: push edx
  loc_004210CA: lea edx, var_54
  loc_004210CD: push ecx
  loc_004210CE: push edx
  loc_004210CF: mov var_84, 00004008h
  loc_004210D9: call [00401124h] ; rtcSplit
  loc_004210DF: lea edx, var_54
  loc_004210E2: lea ecx, var_24
  loc_004210E5: call [00401014h] ; __vbaVarMove
  loc_004210EB: mov ebx, [004010ACh] ; __vbaRefVarAry
  loc_004210F1: lea eax, var_24
  loc_004210F4: push eax
  loc_004210F5: call ebx
  loc_004210F7: mov ecx, [eax]
  loc_004210F9: push ecx
  loc_004210FA: push 00000001h
  loc_004210FC: call [00401144h] ; __vbaUbound
  loc_00421102: mov esi, [004010ECh] ; __vbaI2I4
  loc_00421108: mov ecx, eax
  loc_0042110A: call __vbaI2I4
  loc_0042110C: lea edx, var_24
  loc_0042110F: mov var_A0, eax
  loc_00421115: push edx
  loc_00421116: call ebx
  loc_00421118: mov eax, [eax]
  loc_0042111A: push eax
  loc_0042111B: push 00000001h
  loc_0042111D: call [004010F8h] ; __vbaLbound
  loc_00421123: mov ecx, eax
  loc_00421125: call __vbaI2I4
  loc_00421127: mov esi, [0040109Ch] ; __vbaVarIndexLoad
  loc_0042112D: mov var_14, eax
  loc_00421130: cmp ax, var_A0
  loc_00421137: jg 004212DEh
  loc_0042113D: sub esp, 00000010h
  loc_00421140: mov ecx, 00004002h
  loc_00421145: mov edx, esp
  loc_00421147: mov var_84, ecx
  loc_0042114D: lea eax, var_14
  loc_00421150: push 00000001h
  loc_00421152: mov [edx], ecx
  loc_00421154: mov ecx, var_80
  loc_00421157: mov var_7C, eax
  loc_0042115A: mov [edx+00000004h], ecx
  loc_0042115D: lea ecx, var_24
  loc_00421160: push ecx
  loc_00421161: mov [edx+00000008h], eax
  loc_00421164: mov eax, var_78
  loc_00421167: mov [edx+0000000Ch], eax
  loc_0042116A: lea edx, var_54
  loc_0042116D: push edx
  loc_0042116E: call __vbaVarIndexLoad
  loc_00421170: add esp, 0000001Ch
  loc_00421173: lea edx, var_94
  loc_00421179: lea ecx, var_64
  loc_0042117C: mov var_8C, 00408C0Ch
  loc_00421186: mov var_94, 00000008h
  loc_00421190: call [004011B4h] ; __vbaVarDup
  loc_00421196: push 00000000h
  loc_00421198: lea eax, var_64
  loc_0042119B: push FFFFFFFFh
  loc_0042119D: lea ecx, var_54
  loc_004211A0: push eax
  loc_004211A1: lea edx, var_40
  loc_004211A4: push ecx
  loc_004211A5: push edx
  loc_004211A6: call [00401148h] ; __vbaStrVarVal
  loc_004211AC: push eax
  loc_004211AD: lea eax, var_74
  loc_004211B0: push eax
  loc_004211B1: call [00401124h] ; rtcSplit
  loc_004211B7: lea edx, var_74
  loc_004211BA: lea ecx, var_34
  loc_004211BD: call [00401014h] ; __vbaVarMove
  loc_004211C3: lea ecx, var_40
  loc_004211C6: call [004011F4h] ; __vbaFreeStr
  loc_004211CC: lea ecx, var_64
  loc_004211CF: lea edx, var_54
  loc_004211D2: push ecx
  loc_004211D3: push edx
  loc_004211D4: push 00000002h
  loc_004211D6: call [00401038h] ; __vbaFreeVarList
  loc_004211DC: add esp, 0000000Ch
  loc_004211DF: lea eax, var_34
  loc_004211E2: push eax
  loc_004211E3: call ebx
  loc_004211E5: mov ecx, [eax]
  loc_004211E7: push ecx
  loc_004211E8: push 00000001h
  loc_004211EA: call [004010F8h] ; __vbaLbound
  loc_004211F0: sub esp, 00000010h
  loc_004211F3: mov ecx, 00000003h
  loc_004211F8: mov edx, esp
  loc_004211FA: mov var_84, ecx
  loc_00421200: mov var_7C, eax
  loc_00421203: push 00000001h
  loc_00421205: mov [edx], ecx
  loc_00421207: mov ecx, var_80
  loc_0042120A: mov [edx+00000004h], ecx
  loc_0042120D: lea ecx, var_34
  loc_00421210: push ecx
  loc_00421211: mov [edx+00000008h], eax
  loc_00421214: mov eax, var_78
  loc_00421217: mov [edx+0000000Ch], eax
  loc_0042121A: lea edx, var_54
  loc_0042121D: push edx
  loc_0042121E: call __vbaVarIndexLoad
  loc_00421220: add esp, 0000001Ch
  loc_00421223: push eax
  loc_00421224: call [00401030h] ; __vbaStrVarMove
  loc_0042122A: mov edx, eax
  loc_0042122C: lea ecx, var_3C
  loc_0042122F: call [004011D0h] ; __vbaStrMove
  loc_00421235: lea ecx, var_54
  loc_00421238: call [00401020h] ; __vbaFreeVar
  loc_0042123E: lea eax, var_34
  loc_00421241: push eax
  loc_00421242: call ebx
  loc_00421244: mov ecx, [eax]
  loc_00421246: push ecx
  loc_00421247: push 00000001h
  loc_00421249: call [00401144h] ; __vbaUbound
  loc_0042124F: sub esp, 00000010h
  loc_00421252: mov ecx, 00000003h
  loc_00421257: mov edx, esp
  loc_00421259: mov var_84, ecx
  loc_0042125F: mov var_7C, eax
  loc_00421262: push 00000001h
  loc_00421264: mov [edx], ecx
  loc_00421266: mov ecx, var_80
  loc_00421269: mov [edx+00000004h], ecx
  loc_0042126C: lea ecx, var_34
  loc_0042126F: push ecx
  loc_00421270: mov [edx+00000008h], eax
  loc_00421273: mov eax, var_78
  loc_00421276: mov [edx+0000000Ch], eax
  loc_00421279: lea edx, var_54
  loc_0042127C: push edx
  loc_0042127D: call __vbaVarIndexLoad
  loc_0042127F: add esp, 0000001Ch
  loc_00421282: push eax
  loc_00421283: call [00401030h] ; __vbaStrVarMove
  loc_00421289: mov edx, eax
  loc_0042128B: lea ecx, var_38
  loc_0042128E: call [004011D0h] ; __vbaStrMove
  loc_00421294: lea ecx, var_54
  loc_00421297: call [00401020h] ; __vbaFreeVar
  loc_0042129D: mov eax, [edi]
  loc_0042129F: lea ecx, var_44
  loc_004212A2: push ecx
  loc_004212A3: lea edx, var_38
  loc_004212A6: lea ecx, var_3C
  loc_004212A9: push edx
  loc_004212AA: push ecx
  loc_004212AB: push edi
  loc_004212AC: call [eax+00000034h]
  loc_004212AF: test eax, eax
  loc_004212B1: jge 004212C2h
  loc_004212B3: push 00000034h
  loc_004212B5: push 00405B8Ch
  loc_004212BA: push edi
  loc_004212BB: push eax
  loc_004212BC: call [0040105Ch] ; __vbaHresultCheckObj
  loc_004212C2: lea ecx, var_44
  loc_004212C5: call [004011F0h] ; __vbaFreeObj
  loc_004212CB: mov eax, 00000001h
  loc_004212D0: add ax, var_14
  loc_004212D4: jo 00421345h
  loc_004212D6: mov var_14, eax
  loc_004212D9: jmp 00421130h
  loc_004212DE: push 00421330h
  loc_004212E3: jmp 0042130Fh
  loc_004212E5: lea ecx, var_40
  loc_004212E8: call [004011F4h] ; __vbaFreeStr
  loc_004212EE: lea ecx, var_44
  loc_004212F1: call [004011F0h] ; __vbaFreeObj
  loc_004212F7: lea edx, var_74
  loc_004212FA: lea eax, var_64
  loc_004212FD: push edx
  loc_004212FE: lea ecx, var_54
  loc_00421301: push eax
  loc_00421302: push ecx
  loc_00421303: push 00000003h
  loc_00421305: call [00401038h] ; __vbaFreeVarList
  loc_0042130B: add esp, 00000010h
  loc_0042130E: ret
  loc_0042130F: mov esi, [00401020h] ; __vbaFreeVar
  loc_00421315: lea ecx, var_24
  loc_00421318: call __vbaFreeVar
  loc_0042131A: lea ecx, var_34
  loc_0042131D: call __vbaFreeVar
  loc_0042131F: mov esi, [004011F4h] ; __vbaFreeStr
  loc_00421325: lea ecx, var_38
  loc_00421328: call __vbaFreeStr
  loc_0042132A: lea ecx, var_3C
  loc_0042132D: call __vbaFreeStr
  loc_0042132F: ret
  loc_00421330: mov ecx, var_10
  loc_00421333: pop edi
  loc_00421334: pop esi
  loc_00421335: xor eax, eax
  loc_00421337: mov fs:[00000000h], ecx
  loc_0042133E: pop ebx
  loc_0042133F: mov esp, ebp
  loc_00421341: pop ebp
  loc_00421342: retn 0008h
End Sub
