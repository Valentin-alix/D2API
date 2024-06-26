from EzreD2Shared.shared.enums import ToDirection


MAP_WIDTH = 14
MAP_HEIGHT = 20
MAP_CELLS_COUNT = 560


def getBorderCells(direction: ToDirection):
    currentlyCheckedCellX = None
    currentlyCheckedCellY = None

    if direction in [
        ToDirection.RIGHT,
        ToDirection.RIGHT_BOT,
        ToDirection.RIGHT_TOP,
    ]:
        currentlyCheckedCellX = MAP_WIDTH - 1
        currentlyCheckedCellY = MAP_WIDTH - 1

    elif direction in [
        ToDirection.LEFT,
        ToDirection.LEFT_BOT,
        ToDirection.LEFT_TOP,
    ]:
        currentlyCheckedCellX = 0
        currentlyCheckedCellY = 0

    elif direction in [
        ToDirection.BOT,
        ToDirection.BOT_LEFT,
        ToDirection.BOT_RIGHT,
    ]:
        currentlyCheckedCellX = MAP_HEIGHT - 1
        currentlyCheckedCellY = -(MAP_HEIGHT - 1)

    else:
        currentlyCheckedCellX = 0
        currentlyCheckedCellY = 0

    res = []

    if direction in [
        ToDirection.RIGHT,
        ToDirection.RIGHT_BOT,
        ToDirection.RIGHT_TOP,
    ] or direction in [
        ToDirection.LEFT,
        ToDirection.LEFT_BOT,
        ToDirection.LEFT_TOP,
    ]:
        maxI = MAP_HEIGHT * 2
        for i in range(maxI):
            currentCellId = coordToCellId(currentlyCheckedCellX, currentlyCheckedCellY)
            mapChangeData = 0  # TODO
            if mapChangeData and (
                direction
                in [
                    ToDirection.RIGHT,
                    ToDirection.RIGHT_BOT,
                    ToDirection.RIGHT_TOP,
                ]
                and (
                    mapChangeData & 1
                    or (currentCellId + 1) % (MAP_WIDTH * 2) == 0
                    and mapChangeData & 2
                    or (currentCellId + 1) % (MAP_WIDTH * 2) == 0
                    and mapChangeData & 128
                )
                or direction
                in [
                    ToDirection.LEFT,
                    ToDirection.LEFT_BOT,
                    ToDirection.LEFT_TOP,
                ]
                and (
                    currentlyCheckedCellX == -currentlyCheckedCellY
                    and mapChangeData & 8
                    or mapChangeData & 16
                    or currentlyCheckedCellX == -currentlyCheckedCellY
                    and mapChangeData & 32
                )
            ):
                res.append(currentCellId)
            if not (i % 2):
                currentlyCheckedCellX += 1
            else:
                currentlyCheckedCellY -= 1

    elif direction in [
        ToDirection.BOT,
        ToDirection.BOT_LEFT,
        ToDirection.BOT_RIGHT,
    ] or direction in [ToDirection.TOP, ToDirection.TOP_LEFT, ToDirection.TOP_RIGHT]:
        for i in range(MAP_WIDTH * 2):
            currentCellId = coordToCellId(currentlyCheckedCellX, currentlyCheckedCellY)
            mapChangeData = 0  # TODO
            if mapChangeData and (
                direction
                in [ToDirection.TOP, ToDirection.TOP_LEFT, ToDirection.TOP_RIGHT]
                and (
                    currentCellId < MAP_WIDTH
                    and mapChangeData & 32
                    or mapChangeData & 64
                    or currentCellId < MAP_WIDTH
                    and mapChangeData & 128
                )
                or direction
                in [
                    ToDirection.BOT,
                    ToDirection.BOT_LEFT,
                    ToDirection.BOT_RIGHT,
                ]
                and (
                    currentCellId >= MAP_CELLS_COUNT - MAP_WIDTH
                    and mapChangeData & 2
                    or mapChangeData & 4
                    or currentCellId >= MAP_CELLS_COUNT - MAP_WIDTH
                    and mapChangeData & 8
                )
            ):
                res.append(currentCellId)
            if not (i % 2):
                currentlyCheckedCellX += 1
            else:
                currentlyCheckedCellY += 1

        return res


def coordToCellId(x: int, y: int) -> int:
    return int((x - y) * MAP_WIDTH + y + (x - y) / 2)


def allowsMapChangeToDirection(
    cellId: int, mapChangeData: int, x: int, y: int, direction: ToDirection
):
    if direction in [direction.RIGHT, direction.RIGHT_TOP, direction.RIGHT_BOT]:
        return (
            bool(mapChangeData & 1)
            or ((cellId + 1) % (MAP_WIDTH * 2) == 0 and bool(mapChangeData & 2))
            or ((cellId + 1) % (MAP_WIDTH * 2) == 0 and bool(mapChangeData & 128))
        )
    elif direction in [direction.LEFT, direction.LEFT_TOP, direction.LEFT_BOT]:
        return (
            (x == -y and bool(mapChangeData & 8))
            or bool(mapChangeData & 16)
            or (x == -y and bool(mapChangeData & 32))
        )
    elif direction in [direction.TOP_LEFT, direction.TOP, direction.TOP_RIGHT]:
        return (
            (cellId < MAP_WIDTH and bool(mapChangeData & 32))
            or bool(mapChangeData & 64)
            or (cellId < MAP_WIDTH and bool(mapChangeData & 128))
        )
    elif direction in [direction.BOT_LEFT, direction.BOT, direction.BOT_RIGHT]:
        return (
            (cellId >= MAP_CELLS_COUNT - MAP_WIDTH and bool(mapChangeData & 2))
            or bool(mapChangeData & 4)
            or (cellId >= MAP_CELLS_COUNT - MAP_WIDTH and bool(mapChangeData & 8))
        )

    return False
