# -*- coding: utf-8 -*-

from os import path
from sys import argv
from re import sub
from random import shuffle

# Classe que representa um dado, com sua classe, id e palavras.


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


# Função principal do programa.


def main():
    FILE_PATH = path.abspath(
        path.join(path.dirname(__file__), "preprocessed-data.txt"))

    # Inputs por linha de comando:
    k = -1
    userInformedK = False
    fileName = ""
    userInformedFileName = False
    trainOrTest = ""
    userInformedTrainOrTest = False
    for i, argument in enumerate(argv):
        if i == 1:
            k = int(argument)
            userInformedK = True
        elif i == 2:
            fileName = argument
            userInformedFileName = True
        elif i == 3:
            trainOrTest = argument
            if trainOrTest != "train" and trainOrTest != "test":
                trainOrTest = "train"
            userInformedTrainOrTest = True

    lines = []
    with open(FILE_PATH, mode="r", encoding="utf-8") as file:
        lines = file.readlines()

    dataList = []
    dataClass = ""
    dataId = ""
    words = []

    # Criando os objetos do tipo 'Data'.
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

    # Palavras a serem desconsideradas.
    wordsToDesconsider = ["dell", "notebook",
                          "not", "nov", "quer", "q", "ter", "ach", "agor", "vai", "dess", "inspiron", "precis", "cas", "%", "'s", "'tou"]

    print(f"\nPalavras sendo desconsideradas: {wordsToDesconsider}")

    # Contando a aparição de cada palavra nas frases.
    wordCountDict = {}
    for data in dataList:
        for word in data.words:
            if word[1] not in wordsToDesconsider:
                if word[1] not in wordCountDict:
                    wordCountDict[word[1]] = 1
                else:
                    wordCountDict[word[1]] += 1

    # Definindo quantas palavras serão utilizadas para o bag of words.
    if not userInformedK:
        k = int(input("\nQuantas palavras serão consideradas para o bag of words? "))

    # Gerar conjunto de treino ou teste?
    if not userInformedTrainOrTest:
        trainOrTest = input(
            "Gerar conjunto de treino ou de teste? [train/test]: ")
        if trainOrTest not in ["train", "test"]:
            trainOrTest = "train"

    topWords = sorted(wordCountDict.items(),
                      key=lambda x: x[1], reverse=True)[0:k]

    if trainOrTest == "test":
        shuffle(dataList)
        dataList = dataList[0:int(len(dataList) * 0.2)]

    # Atribuindo 0 ou 1 a cada palavra para indicar se ela está ou não na frase.
    matrixLines = []
    for index, data in enumerate(dataList):
        matrixLines.append([])
        for topWord in topWords:
            found = False
            for word in data.words:
                if topWord[0] == word[1]:
                    matrixLines[index].append(1)
                    found = True
                    break
            if not found:
                matrixLines[index].append(0)
        matrixLines[index].append(data.dataClass)

    # Gerando o arquivo ARFF.
    relation = "@relation emotionAnalysis\n"
    attributes = ""
    for topWord in topWords:
        attributes += f"@attribute {topWord[0]} {'{0,1}'}\n"
    attributes += "@attribute class {-1,1}\n"
    inputData = "@data\n"
    for line in matrixLines:
        if 1 in line or trainOrTest == "test":
            inputData += ",".join(map(str, line))
            inputData += "\n"
    arffFileContent = f"{relation}\n{attributes}\n{inputData}"

    if not userInformedFileName:
        fileName = input("Digite o nome do arquivo ARFF a ser gerado: ")

    if not fileName.endswith(".arff"):
        fileName += ".arff"

    datasetsDirectory = "train-datasets" if trainOrTest == "train" else "test-datasets"
    with open(path.abspath(
            path.join(path.dirname(__file__), f"{datasetsDirectory}/{fileName}")), mode="w+", encoding="utf-8") as file:
        file.write(arffFileContent)

    print("\n-> Arquivo gerado com sucesso <-\n")


if __name__ == '__main__':
    main()
