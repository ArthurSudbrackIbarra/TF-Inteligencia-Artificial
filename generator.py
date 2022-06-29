# -*- coding: utf-8 -*-

from os import path
from random import shuffle
from sys import argv
from re import sub

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
    for i, argument in enumerate(argv):
        if i == 1:
            k = int(argument)
            userInformedK = True
        elif i == 2:
            fileName = argument
            userInformedFileName = True

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
                          "not", "nov", "quer", "q", "ter", "ach", "agor", "vai", "dess", "inspiron", "1", "precis", "cas", "%", "'s", "'tou"]

    print(f"\nPalavras sendo desconsideradas: {wordsToDesconsider}")

    # TODO: SEPARAR CONJUNTO DE TREINO DO DE TESTE.

    # Embaralhando os dados.
    shuffle(dataList)

    trainDataList = dataList[:int(len(dataList) * 0.7)]
    testDataList = dataList[int(len(dataList) * 0.7):]

    # Contando a aparição de cada palavra nas frases no conjunto de treino.
    trainWordCountDict = {}
    for data in trainDataList:
        for word in data.words:
            if word[1] not in wordsToDesconsider:
                if word[1] not in trainWordCountDict:
                    trainWordCountDict[word[1]] = 1
                else:
                    trainWordCountDict[word[1]] += 1

    # Definindo quantas palavras serão utilizadas para o bag of words.
    if not userInformedK:
        k = int(input("\nQuantas palavras serão consideradas para o bag of words? "))

    if not userInformedFileName:
        fileName = f"{k}-words.arff"

    topWords = sorted(trainWordCountDict.items(),
                      key=lambda x: x[1], reverse=True)[0:k]

    # Atribuindo 0 ou 1 a cada palavra para indicar se ela está ou não na frase (conjunto de treino).
    trainMatrixLines = []
    for index, data in enumerate(trainDataList):
        trainMatrixLines.append([])
        for topWord in topWords:
            found = False
            for word in data.words:
                if topWord[0] == word[1]:
                    trainMatrixLines[index].append(1)
                    found = True
                    break
            if not found:
                trainMatrixLines[index].append(0)
        trainMatrixLines[index].append(data.dataClass)

    # Atribuindo 0 ou 1 a cada palavra para indicar se ela está ou não na frase (conjunto de teste).
    testMatrixLines = []
    for index, data in enumerate(testDataList):
        testMatrixLines.append([])
        for topWord in topWords:
            found = False
            for word in data.words:
                if topWord[0] == word[1]:
                    testMatrixLines[index].append(1)
                    found = True
                    break
            if not found:
                testMatrixLines[index].append(0)
        testMatrixLines[index].append(data.dataClass)

    # Gerando os arquivos ARFF.
    relation = "@relation emotionAnalysis\n"
    attributes = ""
    for topWord in topWords:
        attributes += f"@attribute {topWord[0]} {'{0,1}'}\n"
    attributes += "@attribute class {-1,1}\n"
    trainInputData = "@data\n"
    testInputData = "@data\n"
    for line in trainMatrixLines:
        if 1 in line:
            trainInputData += ",".join(map(str, line))
            trainInputData += "\n"
    for line in testMatrixLines:
        testInputData += ",".join(map(str, line))
        testInputData += "\n"
    trainFileContent = f"{relation}\n{attributes}\n{trainInputData}"
    testFileContent = f"{relation}\n{attributes}\n{testInputData}"

    if not fileName.endswith(".arff"):
        fileName += ".arff"

    with open(path.abspath(
            path.join(path.dirname(__file__), f"train-datasets/{fileName}")), mode="w+", encoding="utf-8") as file:
        file.write(trainFileContent)

    with open(path.abspath(
            path.join(path.dirname(__file__), f"test-datasets/{fileName}")), mode="w+", encoding="utf-8") as file:
        file.write(testFileContent)

    print("\nArquivos gerados com sucesso:\n")
    print(
        f"train-datasets/{fileName}: Arquivo de treino.")
    print(
        f"test-datasets/{fileName}: Arquivo de teste.\n")


if __name__ == '__main__':
    main()
