# -*- coding: utf-8 -*-

from os import path
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

    topWords = sorted(wordCountDict.items(),
                      key=lambda x: x[1], reverse=True)[0:k]

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
    testInputData = inputData
    for line in matrixLines:
        if 1 in line:
            inputData += ",".join(map(str, line))
            inputData += "\n"
        testInputData += ",".join(map(str, line))
        testInputData += "\n"
    trainFileContent = f"{relation}\n{attributes}\n{inputData}"
    testFileContent = f"{relation}\n{attributes}\n{testInputData}"

    if not userInformedFileName:
        fileName = input("Digite o nome dos arquivos ARFF's a serem gerados: ")

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
        f"train-datasets/{fileName}: Arquivo de treino, não considera linhas totalmente zeradas.")
    print(
        f"test-datasets/{fileName}: Arquivo de teste, considera todo o dataset.\n")


if __name__ == '__main__':
    main()
