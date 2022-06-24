from os import path
from re import sub


class Data:
    dataClass: str
    dataId: str
    words: "list[tuple[str, str]]"

    def __init__(self, dataClass: str, dataId: str, words: "list[tuple[str, str]]"):
        self.dataClass = dataClass
        self.dataId = dataId
        self.words = words

    def __str__(self) -> str:
        return f"{self.dataClass} {self.dataId} {self.words}"


def main():
    FILE_PATH = path.abspath(
        path.join(path.dirname(__file__), "preprocessado.txt"))

    lines = []
    with open(FILE_PATH, mode="r", encoding="utf-8") as file:
        lines = file.readlines()

    dataList = []

    dataClass = ""
    dataId = ""
    words = []

    for line in lines:
        line = line.strip()
        if line.startswith("<sent>"):
            continue
        elif line.startswith("</sent>"):
            dataList.append(Data(dataClass, dataId, words.copy()))
            words.clear()
        else:
            if line.startswith("<class>"):
                dataClass = line.split(" ")[1]
            elif line.startswith("<id>"):
                dataId = line.split(" ")[1]
            else:
                noExtraSpaces = sub(r"\s+", " ", line)
                words.append(tuple(noExtraSpaces.split(" ")))

    wordCountDict = {}
    for data in dataList:
        for word in data.words:
            if word[1] not in wordCountDict:
                wordCountDict[word[1]] = 1
            else:
                wordCountDict[word[1]] += 1

    k = int(input("Quantos termos serão considerados? (K): "))
    topWords = sorted(wordCountDict.items(),
                      key=lambda x: x[1], reverse=True)[0:k]

    print(dataList[0].words)

    matrixLines = []

    for index, data in enumerate(dataList):
        matrixLines.append([])
        for topWord in topWords:
            for word in data.words:
                if topWord[0] == word[1]:
                    matrixLines[index].append(1)
                    break
            if len(matrixLines[index]) == 0:
                matrixLines[index].append(0)

    print(matrixLines)



if __name__ == '__main__':
    main()
