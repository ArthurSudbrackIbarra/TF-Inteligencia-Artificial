# -*- coding: utf-8 -*-

from os import path
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

    # Contando a aparição de cada palavra nas frases.
    wordCountDict = {}
    for data in dataList:
        for word in data.words:
            if word[1] not in wordCountDict:
                wordCountDict[word[1]] = 1
            else:
                wordCountDict[word[1]] += 1

    # Definindo quantas palavras serão utilizadas para o bag of words.
    k = int(input("Quantos termos serão considerados? (K): "))
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
        attributes += f"@attribute {topWord[0]} numeric\n"
    attributes += "@attribute class {-1,1}\n"
    inputData = "@data\n"
    for line in matrixLines:
        inputData += ",".join(map(str, line))
        inputData += "\n"
    with open(path.abspath(
            path.join(path.dirname(__file__), "train-dataset.arff")), mode="w+", encoding="utf-8") as file:
        file.write(relation + "\n")
        file.write(attributes + "\n")
        file.write(inputData)

    print("Arquivo gerado com sucesso!")


if __name__ == '__main__':
    main()
