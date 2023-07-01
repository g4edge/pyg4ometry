import T114_physical_reflection_x


def Test(vis=False, interactive=False, n_slice=20, n_stack=20, scale=[1, -1, 1]):
    return T114_physical_reflection_x.Test(
        vis, interactive, n_slice, n_stack, scale, title="T115_physical_reflection_y"
    )


if __name__ == "__main__":
    Test()
