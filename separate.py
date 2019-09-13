# coding: utf-8

import glob
import csv
import os
import sys
import datetime

# データの追加処理と削除判定
def colcOutputFile(outputFile):
	cnt = 0
	with open(outputFile, mode="r") as op:
		shirasuSum = loSum = loNum = laSum = laNum = 0 # 初期化
		for line in op:
			cnt  += 1
			data        = line.split(",")
			shirasuSum += float(data[5]) # シラス
			loSum      += float(data[2]) # 緯度
			laSum      += float(data[3]) # 経度
	# 付属情報の書き込み
	with open(outputFile, mode="a") as op:
		op.write(",".join(["シラス魚群断面積合計", str(shirasuSum)])+"\n")
		op.write(",".join(["緯度平均", str(loSum/float(cnt))])+"\n")
		op.write(",".join(["経度平均", str(laSum/float(cnt))])+"\n")

	# データが1行以下の場合は削除
	if cnt <= 1:
		outputFile = "./output/" + str(fileName) + "_" + str(fileNum) + "回目.csv"
		if os.path.exists(outputFile):
			os.remove(outputFile)
		return 1
	print(outputFile + "に書き込み完了！")
	return 0

# 指定したディレクトリの最終行にデータを追加
def addRowData(outputFile, row):
	with open(outputFile, mode="a") as op:
		op.write(",".join(row)+"\n")

# 利用方法
def printHelp():
	print("""
第一引数に分割したい基準のノット数を入れてください
利用例) 2ノットで分割して出力する場合
$ python separate.py 2""")
	exit()

### メイン処理 ###
# 引数チェック
args = sys.argv
if len(args) == 1 or args[1] == "-h":
	printHelp()

# 分割基準のnote数
st_knot = args[1]
print("基準値2ノットで分割します")

files = glob.glob("./input/*")

# ファイルごとに処理
for filePath in files:
	print(filePath + "処理中...")
	outputFlag = 0
	fileNum    = 1
	outputTmp = os.path.basename(filePath)
	fileName, ext = os.path.splitext(outputTmp)

	# ファイルの定形を定義
	outputFile = "./output/" + str(fileName) + "_%s回目.csv"

	# すでにファイルが作成されている場合は削除
	if os.path.exists(outputFile % fileNum):
		os.remove(outputFile % fileNum)

	with open(filePath,"r") as f:
		reader = csv.reader(f)

		# 行ごとに処理
		header = 0
		for row in reader :
			# ファイルの1行目の場合はスキップ
			if header == 0:
				header = 1
				continue

			# CSV側の情報
			date      = row[0]     # 日付
			time      = row[1]     # 時間
			longitude = row[2]     # 緯度
			latitude  = row[3]     # 経度
			speed     = row[4]     # 船速
			shirasuDa = row[5]     # シラス魚群断面積
			if speed == "":
				continue

			# 出力の判定
			# 速度がst_knotより早かった場合
			if float(speed) > float(st_knot):
				# 書き込み中だった場合
				if outputFlag == 1:
					outputFlag = 0
					# 5分以上継続していたかチェック
					if endTime - startTime < 500:
						# 5分間以上継続指定なかった場合はファイルを削除
						os.remove(outputFile % fileNum)
						continue
					# シラス魚群断面積の和を緯度、経度平均を求める
					result = colcOutputFile(outputFile % fileNum)
					if result == 1: # 0:成功 1:失敗
						continue

					# 出力するファイル番号を変更
					fileNum += 1

					# その際すでにファイルがあれば先に削除
					if os.path.exists(outputFile % fileNum):
						os.remove(outputFile % fileNum)
					continue
				# 書き込み中でない場合
				else:
					outputFlag = 0
					continue
			# 速度がst_knot以下だった場合
			# 書き込み中だった場合
			if outputFlag == 1:
				endTime = int(time)
				addRowData(outputFile % fileNum, row)
				continue
			# 新しいファイルに書き込む場合
			else:
				outputFlag = 1
				startTime = int(time)
				addRowData(outputFile % fileNum, row)
				continue

# 最終ファイルに対する処理
# 5分以上継続していたかチェック
if endTime - startTime < 500:
	# 5分間以上継続指定なかった場合はファイルを削除
	os.remove(outputFile % fileNum)
# シラス魚群断面積の和を緯度、経度平均を求める
else:
	colcOutputFile(outputFile % fileNum)
print("正常終了")
# 処理終了
